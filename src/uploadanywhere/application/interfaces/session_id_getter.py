import typing as t

from litestar import Request


class SessionIDGetter(t.Protocol):
    def __init__(self, request: Request) -> None: ...
    def get(self) -> None | str: ...
