import typing as t

import pytest
from asyncpg import Connection
from dishka import AsyncContainer, make_async_container
from dishka.integrations.litestar import LitestarProvider

from tests.core.ioc import FakeAppProvider
from uploadanywhere.infrastructure.postgres.engine import Engine
from uploadanywhere.main.config import Config
from uploadanywhere.main.ioc import CommandProcessorsProvider


@pytest.fixture
def ioc_provider() -> type[FakeAppProvider]:
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
