import typing as t

from asyncpg import Connection
from dishka import AnyOf, Provider, Scope, from_context, provide
from uuid6 import UUID, uuid7

from uploadanywhere.application.command_processors.auth_user_processor import AuthUserCommand, AuthUserProcessor
from uploadanywhere.application.command_processors.create_user_processor import CreateUserCommand, CreateUserFactory
from uploadanywhere.application.command_processors.update_user_processor import (
    UpdateUserCommand,
    UpdateUserFactory,
)
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.id_generator import IDGenerator
from uploadanywhere.application.interfaces.identity_provider import IdentityProvider
from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter
from uploadanywhere.application.interfaces.uow import AsyncUoW, UoWCommitter
from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.session_repository import SessionRepository
from uploadanywhere.domain.interfaces.user_repository import UserRepository
from uploadanywhere.domain.services import UserCreator
from uploadanywhere.infrastructure.hashers.pbkdf2_hasher import PBKDF2PasswordHasher
from uploadanywhere.infrastructure.http_session_manager import HTTPSessionManager
from uploadanywhere.infrastructure.identity_provider import SessionIdentityProvider
from uploadanywhere.infrastructure.litestar_session_manager import LitestarSessionManager
from uploadanywhere.infrastructure.postgres.data_mappers import DataMappersRegistry, UserMapper
from uploadanywhere.infrastructure.postgres.data_mappers.session_mapper import SessionMapper
from uploadanywhere.infrastructure.postgres.engine import Engine
from uploadanywhere.infrastructure.postgres.repositories.session_repository import SessionRepositoryImpl
from uploadanywhere.infrastructure.postgres.repositories.user_repository import UserRepositoryImpl
from uploadanywhere.infrastructure.postgres.uow import UnitOfWork
from uploadanywhere.infrastructure.session_id_getter import SessionIDGetterImpl
from uploadanywhere.main.config import AuthConfig, Config


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_auth_config(self, config: Config) -> AuthConfig:
        return config.auth

    @provide(scope=Scope.APP)
    def get_id_generator(self) -> IDGenerator[UUID]:
        return uuid7

    @provide(scope=Scope.APP)
    async def get_asyncpg_engine(self, config: Config) -> Engine:
        return await Engine.create(config.postgres.dsn)

    @provide(scope=Scope.REQUEST)
    async def get_connection(self, db: Engine) -> t.AsyncIterable[Connection]:
        async with db.acquire() as connection:
            yield t.cast("Connection", connection)

    @provide(scope=Scope.REQUEST)
    def get_registry(self, connection: Connection) -> DataMappersRegistry:
        registry: DataMappersRegistry = DataMappersRegistry()
        registry.add_mapper(UserMapper(connection), entity_type=User)
        registry.add_mapper(SessionMapper(connection), entity_type=Session)
        return registry

    @provide(scope=Scope.REQUEST)
    def get_uow(
        self,
        connection: Connection,
        registry: DataMappersRegistry,
    ) -> AnyOf[AsyncUoW, UoWRegistrator, UoWCommitter]:
        return UnitOfWork(registry=registry, connection=connection)

    password_hasher = provide(PBKDF2PasswordHasher, scope=Scope.APP, provides=PasswordHasher)

    user_repository = provide(UserRepositoryImpl, scope=Scope.REQUEST, provides=UserRepository)
    session_repository = provide(SessionRepositoryImpl, scope=Scope.REQUEST, provides=SessionRepository)

    identity_provider = provide(SessionIdentityProvider, scope=Scope.REQUEST, provides=IdentityProvider)
    session_id_getter = provide(SessionIDGetterImpl, scope=Scope.REQUEST, provides=SessionIDGetter)

    litestar_session_manager = provide(LitestarSessionManager, scope=Scope.REQUEST)
    http_session_manager = provide(HTTPSessionManager, scope=Scope.REQUEST)


class CommandProcessorsProvider(Provider):
    user_creator = provide(UserCreator, scope=Scope.REQUEST)
    create_user = provide(
        CreateUserFactory.execute,
        scope=Scope.REQUEST,
        provides=CommandProcessor[CreateUserCommand, UserId],
    )
    auth_user = provide(AuthUserProcessor, scope=Scope.REQUEST, provides=CommandProcessor[AuthUserCommand, UserId])
    update_user = provide(
        UpdateUserFactory.execute,
        scope=Scope.REQUEST,
        provides=CommandProcessor[UpdateUserCommand, None],
    )
