import typing as t

import pytest
from asyncpg import Connection
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import LitestarProvider

from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.infrastructure.hashers.md5_hasher import MD5PasswordHasher
from uploadanywhere.infrastructure.postgres.engine import Engine
from uploadanywhere.main.config import Config
from uploadanywhere.main.ioc import AppProvider, CommandProcessorsProvider


class FakeAppProvider(AppProvider):
    def __init__(self, db: Engine, con: Connection) -> None:
        super().__init__()
        self.db = db
        self.con = con

    @provide(scope=Scope.APP)
    def get_asyncpg_engine(self) -> Engine:
        return self.db

    @provide(scope=Scope.REQUEST)
    def get_connection(self) -> Connection:
        return self.con

    password_hasher = provide(MD5PasswordHasher, scope=Scope.APP, provides=PasswordHasher)


@pytest.fixture
def ioc_provider() -> type[Provider]:
    return FakeAppProvider


@pytest.fixture
async def container(
    db: Engine,
    con: Connection,
    ioc_provider: type[FakeAppProvider],
) -> t.AsyncGenerator[AsyncContainer, None]:
    config: Config = Config()
    container = make_async_container(
        ioc_provider(db=db, con=con), LitestarProvider(), CommandProcessorsProvider(), context={Config: config}
    )
    yield container
    await container.close()


@pytest.fixture
async def rs_container(container: AsyncContainer) -> t.AsyncGenerator[AsyncContainer, None]:
    async with container() as nested_container:
        yield nested_container
