import typing as t
from datetime import datetime

from uploadanywhere.domain.entities.base import Entity, UoWRegistrator
from uploadanywhere.domain.identifiers import SessionId, UserId


class Session(Entity[SessionId]):
    id: SessionId
    user_id: UserId
    expires_at: datetime

    def __init__(self, uow: UoWRegistrator, session_id: SessionId, user_id: UserId, expires_at: datetime) -> None:
        super().__init__(uow=uow)
        self.id = session_id
        self.user_id = user_id
        self.expires_at = expires_at

    @classmethod
    def create(cls, uow: UoWRegistrator, session_id: SessionId, user_id: UserId, expires_at: datetime) -> t.Self:
        session = cls(uow=uow, session_id=session_id, user_id=user_id, expires_at=expires_at)
        session.mark_new()
        return session
