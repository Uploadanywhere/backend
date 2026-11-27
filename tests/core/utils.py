__all__ = ("AiterMock", "Any", "dt")

import datetime
import typing as t
from dataclasses import dataclass


@dataclass
class Any:  # ruff: ignore[eq-without-hash]
    typeof: t.Any

    def __eq__(self, another: object) -> bool:
        return isinstance(another, self.typeof)


def dt(date_string: str) -> datetime.date | datetime.datetime:
    if len(date_string) > 10:
        return datetime.datetime.fromisoformat(date_string)
    return datetime.date.fromisoformat(date_string)


class AiterMock:
    def __init__(self, values: t.Iterable[t.Any]) -> None:
        self.values = iter(values)

    def __aiter__(self) -> AiterMock:
        return self

    async def __anext__(self) -> t.Any:
        try:
            return self.values.__next__()
        except StopIteration as e:
            raise StopAsyncIteration from e

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> AiterMock:
        return self
