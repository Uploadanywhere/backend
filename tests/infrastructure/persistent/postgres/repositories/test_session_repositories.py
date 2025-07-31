import pytest
from dishka import AsyncContainer
from freezegun.api import FrozenDateTimeFactory
from uuid6 import uuid7

from tests.core.utils import dt
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.identifiers import SessionId
from uploadanywhere.domain.interfaces.session_repository import SessionRepository


@pytest.fixture
async def session_repository(rs_container: AsyncContainer) -> SessionRepository:
    return await rs_container.get(SessionRepository)


async def test_fetch_session_with_id(session_repository: SessionRepository, db_session: Session) -> None:
    got = await session_repository.with_id(db_session.id)

    assert got == db_session


async def test_fetch_session_with_id_if_session_not_found(
    session_repository: SessionRepository, session: Session
) -> None:
    got = await session_repository.with_id(session.id)  # User not found because it doesn't save in the database

    assert got is None


@pytest.mark.usefixtures("db_session")
async def test_fetch_session_with_id_when_id_is_wrong(session_repository: SessionRepository) -> None:
    got = await session_repository.with_id(SessionId(uuid7()))

    assert got is None


async def test_fetch_active_session_with_id(session_repository: SessionRepository, db_session: Session) -> None:
    got = await session_repository.active_with_id(db_session.id)

    assert got == db_session


async def test_fetch_active_session_with_id_if_session_not_found(
    session_repository: SessionRepository,
    session: Session,
) -> None:
    got = await session_repository.active_with_id(session.id)  # User not found because it doesn't save in the database

    assert got is None


@pytest.mark.usefixtures("db_session")
async def test_fetch_session_active_with_id_when_id_is_wrong(session_repository: SessionRepository) -> None:
    got = await session_repository.active_with_id(SessionId(uuid7()))

    assert got is None


@pytest.mark.freeze_time("2021-07-20T18:30:00Z")
async def test_fetch_session_active_with_id_when_session_expired(
    session_repository: SessionRepository,
    freezer: FrozenDateTimeFactory,
    db_session: Session,
) -> None:
    freezer.move_to("2021-07-21T18:30:00Z")

    got = await session_repository.active_with_id(db_session.id)

    assert db_session.expires_at == dt("2021-07-21T18:30:00Z")
    assert got is None


@pytest.mark.freeze_time("2021-07-20T18:30:00Z")
async def test_fetch_session_active_with_id_when_session_live_1_second(
    session_repository: SessionRepository,
    freezer: FrozenDateTimeFactory,
    db_session: Session,
) -> None:
    freezer.move_to("2021-07-21T18:29:59Z")  # 1 second before expiration

    got = await session_repository.active_with_id(db_session.id)

    assert db_session.expires_at == dt("2021-07-21T18:30:00Z")
    assert got == db_session
