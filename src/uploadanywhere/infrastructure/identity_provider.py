from uuid6 import UUID

from uploadanywhere.application.interfaces.identity_provider import IdentityProvider
from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.identifiers import SessionId, UserId
from uploadanywhere.domain.interfaces.session_repository import SessionRepository
from uploadanywhere.domain.interfaces.user_repository import UserRepository
from uploadanywhere.infrastructure.exceptions import UnauthorizedError


class SessionIdentityProvider(IdentityProvider):
    def __init__(
        self,
        session_id_getter: SessionIDGetter,
        user_repository: UserRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._session_id_getter = session_id_getter
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._active_session: Session | None = None

    async def _get_active_session(self) -> Session:
        if self._active_session:
            return self._active_session

        session_id = self._session_id_getter.get()
        if not session_id:
            raise UnauthorizedError("Unauthorized")

        active_session = await self._session_repository.active_with_id(SessionId(UUID(session_id)))
        if not active_session:
            raise UnauthorizedError("Unauthorized")

        self._active_session = active_session
        return active_session

    async def get_current_user_id(self) -> UserId:
        active_session = await self._get_active_session()
        return UserId(active_session.user_id)
