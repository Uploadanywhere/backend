import pytest
from asyncpg import Connection

from uploadanywhere.domain.entities.base import Entity
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.interfaces import AsyncDataMapper
from uploadanywhere.infrastructure.exceptions import CyclicDependencyError, MapperNotFoundError
from uploadanywhere.infrastructure.postgres.data_mappers import UserMapper
from uploadanywhere.infrastructure.postgres.data_mappers.registry import (
    DataMappersRegistry,
)


class MapperA(AsyncDataMapper):
    pass


class MapperB(AsyncDataMapper):
    pass


class MapperC(AsyncDataMapper):
    pass


class MapperD(AsyncDataMapper):
    pass


class EntityA(Entity):
    pass


class EntityB(Entity):
    pass


class EntityC(Entity):
    pass


class EntityD(Entity):
    pass


@pytest.fixture
def registry() -> DataMappersRegistry:
    return DataMappersRegistry()


def test_add_mapper_successfully(registry: DataMappersRegistry, con: Connection) -> None:
    mock_mapper = MapperA(connection=con)  # type: ignore[abstract]
    registry.add_mapper(mock_mapper, entity_type=User)

    assert registry._mappers[MapperA] == mock_mapper


def test_get_correct_mapper_for_registered_entity_type(registry: DataMappersRegistry, con: Connection) -> None:
    user_mapper = UserMapper(connection=con)

    registry.add_mapper(user_mapper, entity_type=User)

    retrieved_mapper = registry.get(User)

    assert retrieved_mapper == user_mapper
    assert isinstance(retrieved_mapper, UserMapper)


def test_get_mapper_for_unregistered_entity_raises_error(registry: DataMappersRegistry) -> None:
    class UnregisteredEntity(Entity):
        pass

    with pytest.raises(MapperNotFoundError, match=f"Mapper for {UnregisteredEntity} not registered"):
        registry.get(UnregisteredEntity)


def test_add_multiple_mappers(registry: DataMappersRegistry, con: Connection) -> None:
    mapper1 = MapperA(connection=con)  # type: ignore[abstract]
    mapper2 = MapperB(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper1, entity_type=Entity)
    registry.add_mapper(mapper2, entity_type=Entity)

    assert registry._mappers[MapperA] == mapper1
    assert registry._mappers[MapperB] == mapper2


def test_override_existing_mapper(registry: DataMappersRegistry, con: Connection) -> None:
    original_mapper = UserMapper(connection=con)
    registry.add_mapper(original_mapper, entity_type=User)

    new_mapper = UserMapper(connection=con)
    registry.add_mapper(new_mapper, entity_type=User)

    retrieved_mapper = registry.get(User)
    assert retrieved_mapper == new_mapper
    assert retrieved_mapper != original_mapper


def test_registry_handles_multiple_entity_types(registry: DataMappersRegistry, con: Connection) -> None:
    user_mapper = UserMapper(connection=con)
    custom_mapper = MapperA(connection=con)  # type: ignore[abstract]

    registry.add_mapper(user_mapper, entity_type=User)
    registry.add_mapper(custom_mapper, entity_type=EntityA)
    registry._keys[EntityA] = MapperA

    retrieved_user_mapper = registry.get(User)
    retrieved_custom_mapper = registry.get(EntityA)

    assert isinstance(retrieved_user_mapper, UserMapper)
    assert isinstance(retrieved_custom_mapper, MapperA)
    assert retrieved_user_mapper == user_mapper
    assert retrieved_custom_mapper == custom_mapper


def test_registry_state_consistency(registry: DataMappersRegistry, con: Connection) -> None:
    mapper1 = MapperA(connection=con)  # type: ignore[abstract]
    mapper2 = MapperB(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper1, entity_type=EntityA)
    registry.add_mapper(mapper2, entity_type=EntityA)

    assert len(registry._mappers) == 2
    assert registry._mappers[MapperA] == mapper1
    assert registry._mappers[MapperB] == mapper2

    del registry._mappers[MapperA]

    assert len(registry._mappers) == 1
    assert MapperA not in registry._mappers
    assert registry._mappers[MapperB] == mapper2

    registry.add_mapper(mapper1, entity_type=EntityA)

    assert len(registry._mappers) == 2
    assert registry._mappers[MapperA] == mapper1
    assert registry._mappers[MapperB] == mapper2


def test_resolve_dependencies_returns_empty_when_no_mappers_registered(registry: DataMappersRegistry) -> None:
    result = registry.resolve_dependencies()
    assert result == []


def test_resolve_dependencies_raises_cyclic_dependency_error(registry: DataMappersRegistry, con: Connection) -> None:
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper_a, entity_type=EntityA, dependencies=[MapperB])
    registry.add_mapper(mapper_b, entity_type=EntityB, dependencies=[MapperA])

    with pytest.raises(CyclicDependencyError, match="Cyclic dependency detected: MapperA"):
        registry.resolve_dependencies()


def test_resolve_dependencies_no_dependencies(registry: DataMappersRegistry, con: Connection) -> None:
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper_a, entity_type=EntityA)
    registry.add_mapper(mapper_b, entity_type=EntityB)

    assert registry.resolve_dependencies() == [{EntityA: mapper_a}, {EntityB: mapper_b}]


def test_resolve_dependencies_with_linear_dependencies(registry: DataMappersRegistry, con: Connection) -> None:
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]
    mapper_c = MapperC(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper_a, entity_type=EntityA, dependencies=[])
    registry.add_mapper(mapper_b, entity_type=EntityB, dependencies=[MapperA])
    registry.add_mapper(mapper_c, entity_type=EntityC, dependencies=[MapperB])

    assert registry.resolve_dependencies() == [{EntityA: mapper_a}, {EntityB: mapper_b}, {EntityC: mapper_c}]


def test_resolve_dependencies_with_complex_acyclic_dependencies(registry: DataMappersRegistry, con: Connection) -> None:
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]
    mapper_c = MapperC(connection=con)  # type: ignore[abstract]
    mapper_d = MapperD(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper_a, entity_type=EntityA, dependencies=[])
    registry.add_mapper(mapper_b, entity_type=EntityB, dependencies=[MapperA])
    registry.add_mapper(mapper_c, entity_type=EntityC, dependencies=[MapperA, MapperB])
    registry.add_mapper(mapper_d, entity_type=EntityD, dependencies=[MapperB, MapperC])

    assert registry.resolve_dependencies() == [
        {EntityA: mapper_a},
        {EntityB: mapper_b},
        {EntityC: mapper_c},
        {EntityD: mapper_d},
    ]


def test_resolve_dependencies_with_pre_sorted_dependencies(registry: DataMappersRegistry, con: Connection) -> None:
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]
    mapper_c = MapperC(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper_a, entity_type=EntityA, dependencies=[])
    registry.add_mapper(mapper_b, entity_type=EntityB, dependencies=[MapperA])
    registry.add_mapper(mapper_c, entity_type=EntityC, dependencies=[MapperA, MapperB])

    assert registry.resolve_dependencies() == [{EntityA: mapper_a}, {EntityB: mapper_b}, {EntityC: mapper_c}]


def test_resolve_dependencies_with_reverse_order(registry: DataMappersRegistry, con: Connection) -> None:
    mapper_c = MapperC(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]

    registry.add_mapper(mapper_c, entity_type=EntityC, dependencies=[MapperB])
    registry.add_mapper(mapper_b, entity_type=EntityB, dependencies=[MapperA])
    registry.add_mapper(mapper_a, entity_type=EntityA, dependencies=[])

    assert registry.resolve_dependencies() == [{EntityA: mapper_a}, {EntityB: mapper_b}, {EntityC: mapper_c}]


def test_resolve_dependencies_with_shared_dependencies(registry: DataMappersRegistry, con: Connection) -> None:
    class SharedDependencyMapper(AsyncDataMapper):
        pass

    shared_dependency_mapper = SharedDependencyMapper(connection=con)  # type: ignore[abstract]
    mapper_a = MapperA(connection=con)  # type: ignore[abstract]
    mapper_b = MapperB(connection=con)  # type: ignore[abstract]

    registry.add_mapper(shared_dependency_mapper, entity_type=Entity, dependencies=[])
    registry.add_mapper(mapper_a, entity_type=EntityA, dependencies=[SharedDependencyMapper])
    registry.add_mapper(mapper_b, entity_type=EntityB, dependencies=[SharedDependencyMapper])

    assert registry.resolve_dependencies() == [
        {Entity: shared_dependency_mapper},
        {EntityA: mapper_a},
        {EntityB: mapper_b},
    ]
