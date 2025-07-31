import typing as t

T = t.TypeVar("T")


class IDGenerator[T](t.Protocol):
    def __call__(self) -> T: ...
