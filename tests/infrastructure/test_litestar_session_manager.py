import typing as t
from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import AsyncContainer

from tests.core.utils import Any
from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.infrastructure.http_session_manager import HTTPSessionManager
from uploadanywhere.infrastructure.litestar_session_manager import LitestarSessionManager

DEFAULT_TTL_IN_SECONDS = 180 * 24 * 60 * 60  # 180 days


@pytest.fixture
async def session_manager(rs_container: AsyncContainer) -> LitestarSessionManager:
    raw_session_manager = await rs_container.get(HTTPSessionManager)
    session_getter = MagicMock(spec=SessionIDGetter)
    return LitestarSessionManager(
        http_session_manager=raw_session_manager,
        session_id_getter=t.cast("SessionIDGetter", session_getter),
    )


async def test_init_session(session_manager: LitestarSessionManager, db_user: User) -> None:
    response = MagicMock()

    await session_manager.init_session(db_user.id, response)

    response.set_cookie.assert_called_once_with(
        key="session-id",
        value=Any(str),
        httponly=True,
        expires=DEFAULT_TTL_IN_SECONDS,
        secure=True,
    )


async def test_init_session_called_http_session_manager(session_manager: LitestarSessionManager, db_user: User) -> None:
    response = MagicMock()
    session_manager._http_session_manager.init_session = AsyncMock()  # type: ignore[method-assign]

    await session_manager.init_session(db_user.id, response)

    session_manager._http_session_manager.init_session.assert_awaited_with(user_id=db_user.id)


async def test_remove_active_session(session_manager: LitestarSessionManager, db_session: Session) -> None:
    response = MagicMock()
    session_manager._session_id_getter.get = MagicMock(return_value=str(db_session.id))  # type: ignore[method-assign]

    await session_manager.remove_active_session(response=response)

    response.delete_cookie.assert_called_once_with(key="session-id")


async def test_remove_active_session_called_http_session_manager(
    session_manager: LitestarSessionManager,
    db_session: Session,
) -> None:
    response = MagicMock()
    session_manager._http_session_manager.remove_session = AsyncMock()  # type: ignore[method-assign]
    session_manager._session_id_getter.get = MagicMock(return_value=str(db_session.id))  # type: ignore[method-assign]

    await session_manager.remove_active_session(response)

    session_manager._http_session_manager.remove_session.assert_awaited_with(session_id=db_session.id)


async def test_remove_not_existing_session_called_http_session_manager(session_manager: LitestarSessionManager) -> None:
    response = MagicMock()
    session_manager._http_session_manager.remove_session = AsyncMock()  # type: ignore[method-assign]
    session_manager._session_id_getter.get = MagicMock(return_value=None)  # type: ignore[method-assign]

    await session_manager.remove_active_session(response)

    session_manager._http_session_manager.remove_session.assert_not_awaited()
    response.delete_cookie.assert_called_once_with(key="session-id")
