from litestar import Request

from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter


class SessionIDGetterImpl(SessionIDGetter):
    def __init__(self, request: Request) -> None:
        self._request = request

    def get(self) -> str | None:
        return self._request.headers.get("session-id")
