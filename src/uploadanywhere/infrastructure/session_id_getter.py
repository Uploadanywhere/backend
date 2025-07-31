from litestar import Request

from uploadanywhere.application.interfaces.session_id_getter import SessionIDGetter


class SessionIDGetterImpl(SessionIDGetter):
    def __init__(self, request: Request) -> None:
        self._request = request

    def get(self) -> None | str:
        return self._request.headers.get("session-id")
