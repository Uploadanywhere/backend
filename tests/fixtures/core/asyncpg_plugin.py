import typing as t

import pytest
import pytest_asyncio
from asyncpg.pool import PoolConnectionProxy

from uploadanywhere.infrastructure.postgres.engine import Engine


def pytest_configure(config: t.Any) -> None:
    config.addinivalue_line("markers", "asyncpg_engine: configure asyncpg-engine plugin behaviour.")


@pytest.fixture
def asyncpg_engine_cls() -> type[Engine]:
    return Engine


@pytest_asyncio.fixture
async def db(
    request: pytest.FixtureRequest,
    asyncpg_engine_cls: type[Engine],
    postgres_url: str,
) -> t.AsyncGenerator[Engine, None]:
    plugin_config = request.node.get_closest_marker("asyncpg_engine")

    transactional = getattr(plugin_config, "kwargs", {}).get("transactional", True)

    engine = await asyncpg_engine_cls.create(url=postgres_url, use_single_connection=transactional)

    con: PoolConnectionProxy = await engine.acquire()
    tr = con.transaction()
    await tr.start()

    yield engine

    await tr.rollback()
    await engine.release(con, force=transactional)
    await engine.close()


@pytest_asyncio.fixture
async def con(db: Engine) -> t.AsyncGenerator[PoolConnectionProxy, None]:
    async with db.acquire() as connection:
        yield connection
