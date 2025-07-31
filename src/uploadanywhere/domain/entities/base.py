import typing as t


class UoWRegistrator[E](t.Protocol):
    _new: dict[type[E], list[E]]
    _dirty: dict[type[E], list[E]]
    _deleted: dict[type[E], list[E]]

    def register_new(self, *, entity: E) -> None: ...

    def register_dirty(self, *, entity: E) -> None: ...

    def register_deleted(self, *, entity: E) -> None: ...


class Entity[T]:
    id: T

    def __init__(self, uow: UoWRegistrator) -> None:
        self._uow = uow

    def delete(self) -> None:
        self.mark_deleted()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    def mark_dirty(self) -> None:
        self._uow.register_dirty(entity=self)

    def mark_deleted(self) -> None:
        self._uow.register_deleted(entity=self)

    def mark_new(self) -> None:
        self._uow.register_new(entity=self)
