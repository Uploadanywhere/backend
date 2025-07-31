from datetime import UTC, datetime
from uuid import UUID

import pytest
from dishka import AsyncContainer
from uuid6 import uuid7

from tests.core.utils import Any
from tests.factories.sessions import SessionFactory
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import SessionId
from uploadanywhere.infrastructure.http_session_manager import HTTPSessionManager

DEFAULT_TTL_IN_SECONDS = 180 * 24 * 60 * 60  # 180 days


@pytest.fixture
async def session_manager(rs_container: AsyncContainer) -> HTTPSessionManager:
    return await rs_container.get(HTTPSessionManager)


@pytest.mark.freeze_time("2021-07-20T18:30:00Z")
async def test_session_manager_create_session_cookie(
    session_manager: HTTPSessionManager,
    db_user: User,
    session_factory: SessionFactory,
) -> None:
    got = await session_manager.init_session(db_user.id)

    assert await session_factory.fetch_session(got.value) == {
        "expires_at": datetime(2022, 1, 16, 18, 30, tzinfo=UTC),
        "session_id": UUID(got.value),
        "user_id": Any(UUID),
    }


async def test_session_manager_return_session_cookie(session_manager: HTTPSessionManager, db_user: User) -> None:
    got = await session_manager.init_session(db_user.id)

    assert got.key == "session-id"
    assert got.value == Any(str)
    assert got.ttl_in_seconds == DEFAULT_TTL_IN_SECONDS
    assert got.httponly is True
    assert got.secure is True


async def test_session_manager_remove_session_cookie(
    session_manager: HTTPSessionManager,
    db_session: Session,
    session_factory: SessionFactory,
) -> None:
    await session_manager.remove_session(db_session.id)

    assert await session_factory.count_sessions() == 0


async def test_session_manager_remove_not_existed_session_cookie(
    session_manager: HTTPSessionManager,
    session_factory: SessionFactory,
) -> None:
    await session_manager.remove_session(SessionId(uuid7()))

    assert await session_factory.count_sessions() == 0
