from litestar import Response
from uuid6 import UUID

from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter
from uploadanywhere.domain.identifiers import SessionId, UserId
from uploadanywhere.infrastructure.http_session_manager import HTTPSessionManager


class LitestarSessionManager:
    def __init__(self, http_session_manager: HTTPSessionManager, session_id_getter: SessionIDGetter) -> None:
        self._http_session_manager = http_session_manager
        self._session_id_getter = session_id_getter

    async def init_session(self, user_id: UserId, response: Response) -> None:
        session_cookie = await self._http_session_manager.init_session(user_id=user_id)
        response.set_cookie(
            key=session_cookie.key,
            value=session_cookie.value,
            httponly=session_cookie.httponly,
            expires=session_cookie.ttl_in_seconds,
            secure=session_cookie.secure,
        )

    async def remove_active_session(self, response: Response) -> None:
        current_session_id = self._session_id_getter.get()
        if current_session_id:
            await self._http_session_manager.remove_session(session_id=SessionId(UUID(current_session_id)))
        response.delete_cookie(key="session-id")
