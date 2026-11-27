import pytest
from asyncpg import Connection
from dishka import AsyncContainer, Provider, Scope, make_async_container
from dishka.integrations.litestar import LitestarProvider

from tests.core.ioc import FakeAppProvider
from tests.core.utils import Any
from tests.factories.users import UserFactory
from uploadanywhere.application.command_processors.update_user_processor import UpdateUserCommand, UpdateUserProcessor
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.identity_provider import IdentityProvider
from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.exceptions import ValidationError
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository
from uploadanywhere.infrastructure.postgres.engine import Engine
from uploadanywhere.main.config import Config
from uploadanywhere.main.ioc import CommandProcessorsProvider


class FakeIDP(IdentityProvider):
    def __init__(self, user_id: UserId) -> None:
        self._current_user_id = user_id

    async def get_current_user_id(self) -> UserId:
        return self._current_user_id


class FakeIDPProvider(Provider):
    def __init__(self, user_id: UserId) -> None:
        super().__init__()
        self._user_id = user_id
        self.provide(self.identity_provider, scope=Scope.REQUEST, provides=IdentityProvider, override=True)

    def identity_provider(self) -> IdentityProvider:
        return FakeIDP(user_id=self._user_id)


@pytest.fixture
async def uow(rs_container: AsyncContainer) -> AsyncUoW:
    return await rs_container.get(AsyncUoW)


@pytest.fixture
async def processor(rs_container: AsyncContainer, db_user: User) -> UpdateUserProcessor:
    idp = FakeIDP(user_id=db_user.id)
    repo = await rs_container.get(UserRepository)
    return UpdateUserProcessor(user_repository=repo, idp=idp)


async def test_update_user_processor(
    uow: AsyncUoW,
    processor: UpdateUserProcessor,
    user_factory: UserFactory,
    db_user: User,
) -> None:
    command = UpdateUserCommand("new_username")

    await processor.process(command)
    await uow.commit()  # save changes to the database

    updated_user = await user_factory.fetch_user(db_user.id)
    assert updated_user == {
        "email": db_user.email,
        "password": Any(str),
        "user_id": db_user.id,
        "username": "new_username",
    }


async def test_processor_raises_exception_for_none_username(processor: UpdateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        await processor.process(UpdateUserCommand(None))  # type: ignore[arg-type]


async def test_processor_raises_exception_for_empty_username(processor: UpdateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        await processor.process(UpdateUserCommand(""))


async def test_processor_with_transaction_processor_in_chain(
    db: Engine,
    con: Connection,
    user_factory: UserFactory,
    db_user: User,
) -> None:
    container = make_async_container(
        FakeAppProvider(db=db, con=con),
        FakeIDPProvider(user_id=db_user.id),
        LitestarProvider(),
        CommandProcessorsProvider(),
        context={Config: Config()},
    )
    try:
        async with container() as rs_container:
            update_user = await rs_container.get(CommandProcessor[UpdateUserCommand, None])
            await update_user.process(UpdateUserCommand("new_username"))
    finally:
        await container.close()

    updated_user = await user_factory.fetch_user(db_user.id)
    assert updated_user == {
        "email": db_user.email,
        "password": Any(str),
        "user_id": db_user.id,
        "username": "new_username",
    }
