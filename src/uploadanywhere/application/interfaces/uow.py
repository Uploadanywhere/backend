import typing as t

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.interfaces import Registry


class UoWCommitter[C](t.Protocol):
    def __init__(self, registry: Registry, connection: C) -> None: ...
    def commit(self) -> None: ...


class AsyncUoWCommitter[C](t.Protocol):
    def __init__(self, registry: Registry, connection: C) -> None: ...
    async def commit(self) -> None: ...


class UoW[C, E](UoWCommitter[C], UoWRegistrator[E], t.Protocol):
    pass


class AsyncUoW[C, E](AsyncUoWCommitter[C], UoWRegistrator[E], t.Protocol):
    pass
