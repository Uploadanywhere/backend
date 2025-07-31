import typing as t
from unittest.mock import MagicMock

import pytest
from dishka import AsyncContainer
from freezegun.api import FrozenDateTimeFactory

from tests.core.utils import dt
from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.interfaces.session_repository import SessionRepository
from uploadanywhere.domain.interfaces.user_repository import UserRepository
from uploadanywhere.infrastructure.exceptions import UnauthorizedError
from uploadanywhere.infrastructure.identity_provider import SessionIdentityProvider


@pytest.fixture
async def idp(rs_container: AsyncContainer, db_session: Session) -> SessionIdentityProvider:
    user_repo = await rs_container.get(UserRepository)
    session_repo = await rs_container.get(SessionRepository)
    session_id_getter = MagicMock(spec=SessionIDGetter)
    session_id_getter.get.return_value = str(db_session.id)
    return SessionIdentityProvider(
        user_repository=user_repo,
        session_repository=session_repo,
        session_id_getter=t.cast(SessionIDGetter, session_id_getter),
    )


async def test_idp_returns_current_user(idp: SessionIdentityProvider, user: User) -> None:
    got = await idp.get_current_user_id()

    assert got == user.id


async def test_idp_return_none_if_session_id_not_passed(idp: SessionIdentityProvider) -> None:
    idp._session_id_getter.get.return_value = None  # type: ignore[attr-defined]

    with pytest.raises(UnauthorizedError):
        await idp.get_current_user_id()


@pytest.mark.freeze_time("2021-07-20T18:30:00Z")
async def test_idp_return_none_if_session_expired(
    idp: SessionIdentityProvider,
    freezer: FrozenDateTimeFactory,
    db_session: Session,
) -> None:
    freezer.move_to("2021-07-21T18:30:00Z")

    with pytest.raises(UnauthorizedError):
        await idp.get_current_user_id()

    assert db_session.expires_at == dt("2021-07-21T18:30:00Z")


@pytest.mark.freeze_time("2021-07-20T18:30:00Z")
async def test_idp_return_session_if_it_not_expired(
    idp: SessionIdentityProvider,
    freezer: FrozenDateTimeFactory,
    db_session: Session,
) -> None:
    freezer.move_to("2021-07-21T18:29:00Z")  # 1 second before expiration

    got = await idp.get_current_user_id()

    assert db_session.expires_at == dt("2021-07-21T18:30:00Z")
    assert got == db_session.user_id


async def test_idp_raise_error_inside_if_session_id_not_passed(idp: SessionIdentityProvider) -> None:
    idp._session_id_getter.get.return_value = None  # type: ignore[attr-defined]

    with pytest.raises(UnauthorizedError):
        await idp._get_active_session()


async def test_idp_return_active_session_if_exists(idp: SessionIdentityProvider, session: Session) -> None:
    idp._session_id_getter.get.return_value = None  # type: ignore[attr-defined]
    idp._active_session = session

    got = await idp._get_active_session()

    assert got == session
