from datetime import UTC, datetime, timedelta

from uuid6 import UUID

from uploadanywhere.application.interfaces.id_generator import IDGenerator
from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.identifiers import SessionId, UserId
from uploadanywhere.domain.interfaces.session_repository import SessionRepository
from uploadanywhere.main.config import AuthConfig


class SessionCookie:
    def __init__(self, key: str, value: str, httponly: bool, ttl_in_seconds: int, secure: bool) -> None:
        self.key = key
        self.value = value
        self.httponly = httponly
        self.ttl_in_seconds = ttl_in_seconds
        self.secure = secure


class HTTPSessionManager:
    def __init__(
        self,
        uow: AsyncUoW,
        id_generator: IDGenerator[UUID],
        session_repository: SessionRepository,
        config: AuthConfig,
    ) -> None:
        self._uow = uow
        self._id_generator = id_generator
        self._session_repository = session_repository
        self.session_ttl_in_days = config.session_ttl_in_days

    def session_ttl_in_seconds(self) -> int:
        return self.session_ttl_in_days * 24 * 60 * 60  # in seconds

    async def init_session(self, user_id: UserId) -> SessionCookie:
        session = Session.create(
            uow=self._uow,
            session_id=SessionId(self._id_generator()),
            user_id=user_id,
            expires_at=datetime.now(UTC) + timedelta(days=self.session_ttl_in_days),
        )
        await self._uow.commit()
        return SessionCookie(
            key="session-id",
            value=str(session.id),
            httponly=True,
            ttl_in_seconds=self.session_ttl_in_seconds(),
            secure=True,
        )

    async def remove_session(self, session_id: SessionId) -> None:
        session = await self._session_repository.with_id(session_id)
        if session:
            session.delete()
            await self._uow.commit()
