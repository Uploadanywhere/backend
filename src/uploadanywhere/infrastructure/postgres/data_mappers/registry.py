from collections import deque

from uploadanywhere.domain.entities.base import Entity
from uploadanywhere.domain.interfaces import AsyncDataMapper, DataMapper, Registry
from uploadanywhere.infrastructure.exceptions import CyclicDependencyError, MapperNotFoundError


class DataMappersRegistry(Registry):
    def __init__(self) -> None:
        self._mappers: dict[type[DataMapper | AsyncDataMapper], DataMapper | AsyncDataMapper] = {}
        self._keys: dict[type[Entity], type[DataMapper | AsyncDataMapper]] = {}
        self._dependencies: dict[type[DataMapper | AsyncDataMapper], list[type[DataMapper | AsyncDataMapper]]] = {}

    def add_mapper(
        self,
        mapper: DataMapper | AsyncDataMapper,
        entity_type: type[Entity],
        dependencies: list[type[DataMapper | AsyncDataMapper]] | None = None,
    ) -> None:
        self._mappers[type(mapper)] = mapper
        self._keys[entity_type] = type(mapper)
        self._dependencies[type(mapper)] = dependencies or []

    def get(self, entity_type: type[Entity]) -> DataMapper | AsyncDataMapper:
        key = self._keys.get(entity_type)
        if not key:
            raise MapperNotFoundError(f"Mapper for {entity_type} not registered")

        return self._mappers[key]

    def _get_dependencies(
        self, mapper_class: type[DataMapper | AsyncDataMapper]
    ) -> list[type[DataMapper | AsyncDataMapper]]:
        return self._dependencies.get(mapper_class, [])

    def _get_all_mappers(self) -> list[DataMapper | AsyncDataMapper]:
        return list(self._mappers.values())

    def resolve_dependencies(self) -> list[dict[type[Entity], DataMapper | AsyncDataMapper]]:
        visited = set()
        sorted_mappers = []
        stack: deque[type[DataMapper | AsyncDataMapper]] = deque()

        def visit(mapper_class_: type[DataMapper | AsyncDataMapper]) -> None:
            if mapper_class_ in visited:
                return
            if mapper_class_ in stack:
                raise CyclicDependencyError(f"Cyclic dependency detected: {mapper_class_.__name__}")

            stack.append(mapper_class_)

            for dep in self._get_dependencies(mapper_class_):
                visit(dep)

            stack.pop()
            visited.add(mapper_class_)
            sorted_mappers.append(mapper_class_)

        for mapper_class in self._get_all_mappers():
            visit(type(mapper_class))

        return [
            {entity_type: self._mappers[mapper_class]}
            for mapper_class in sorted_mappers
            for entity_type in self._keys
            if self._keys[entity_type] == mapper_class
        ]
