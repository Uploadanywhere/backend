import typing as t


class Registry[M, E](t.Protocol):
    _keys: dict[type[E], type[M]]
    _mappers: dict[type[M], M]
    _dependencies: dict[type[M], list[type[M]]]

    def add_mapper(self, mapper: M, entity_type: E, dependencies: list[M]) -> None: ...

    def get(self, entity_type: type[E]) -> M: ...

    def resolve_dependencies(self) -> list[dict[type[E], M]]: ...
