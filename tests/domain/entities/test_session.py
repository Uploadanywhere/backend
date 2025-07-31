from datetime import UTC, datetime

from uuid6 import uuid7

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import SessionId


def test_delete_session(fake_uow_registrator: UoWRegistrator, user: User) -> None:
    session = Session(
        uow=fake_uow_registrator,
        session_id=SessionId(uuid7()),
        user_id=user.id,
        expires_at=datetime.now(UTC),
    )

    session.delete()

    assert session in fake_uow_registrator._deleted[Session]


def test_create_session(fake_uow_registrator: UoWRegistrator, user: User) -> None:
    session = Session.create(
        uow=fake_uow_registrator,
        session_id=SessionId(uuid7()),
        user_id=user.id,
        expires_at=datetime.now(UTC),
    )

    assert session in fake_uow_registrator._new[Session]
