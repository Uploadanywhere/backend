from datetime import UTC, datetime

import pytest
from asyncpg import Connection
from dishka import AsyncContainer

from tests.factories.sessions import SessionFactory
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.infrastructure.postgres.data_mappers.session_mapper import SessionMapper


@pytest.fixture
async def session_mapper(rs_container: AsyncContainer) -> SessionMapper:
    con = await rs_container.get(Connection)
    return SessionMapper(connection=con)


@pytest.mark.usefixtures("db_user")
async def test_session_mapper_create_all(
    session_mapper: SessionMapper,
    session: Session,
    session_factory: SessionFactory,
) -> None:
    await session_mapper.add_all([session])

    assert await session_factory.fetch_session(session.id) == {
        "expires_at": session.expires_at,
        "session_id": session.id,
        "user_id": session.user_id,
    }


async def test_session_mapper_update_all(
    session_mapper: SessionMapper,
    db_session: Session,
    session_factory: SessionFactory,
) -> None:
    db_session.expires_at = datetime(2222, 2, 22, 22, 22, 22, tzinfo=UTC)

    await session_mapper.update_all([db_session])

    assert await session_factory.fetch_session(db_session.id) == {
        "expires_at": datetime(2222, 2, 22, 22, 22, 22, tzinfo=UTC),
        "session_id": db_session.id,
        "user_id": db_session.user_id,
    }


async def test_session_mapper_delete_all(
    session_mapper: SessionMapper,
    db_session: Session,
    session_factory: SessionFactory,
) -> None:
    await session_mapper.delete_all([db_session])

    assert not await session_factory.fetch_session(db_session.id)
    assert await session_factory.count_sessions() == 0
