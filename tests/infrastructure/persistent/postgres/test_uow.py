from unittest.mock import AsyncMock

import pytest
from asyncpg import Connection

from uploadanywhere.domain.entities.base import Entity
from uploadanywhere.domain.interfaces import AsyncDataMapper
from uploadanywhere.infrastructure.postgres.data_mappers import DataMappersRegistry
from uploadanywhere.infrastructure.postgres.uow import UnitOfWork


class MockEntity(Entity):
    id: int

    def __init__(self, uow: UnitOfWork, id_: int) -> None:
        super().__init__(uow)
        self.id = id_


@pytest.fixture
def mock_connection() -> AsyncMock:
    return AsyncMock(spec=Connection)


@pytest.fixture
def mock_mapper() -> AsyncMock:
    mapper = AsyncMock(spec=AsyncDataMapper)
    mapper.update_all.return_value = AsyncMock()
    mapper.delete_all.return_value = AsyncMock()
    mapper.add_all.return_value = AsyncMock()
    return mapper


@pytest.fixture
def registry(mock_mapper: AsyncDataMapper) -> DataMappersRegistry:
    registry = DataMappersRegistry()
    registry.add_mapper(mock_mapper, entity_type=MockEntity)
    return registry


@pytest.fixture
def uow(registry: DataMappersRegistry, mock_connection: Connection) -> UnitOfWork:
    return UnitOfWork(registry, mock_connection)


@pytest.mark.parametrize("register_as", ["new", "dirty", "deleted"])
def test_register_entity(uow: UnitOfWork, register_as: str) -> None:
    test_entity = MockEntity(uow=uow, id_=1)

    getattr(uow, f"register_{register_as}")(entity=test_entity)

    assert len(getattr(uow, f"_{register_as}")) == 1
    assert MockEntity in getattr(uow, f"_{register_as}")
    assert test_entity in getattr(uow, f"_{register_as}")[MockEntity]
    assert len(getattr(uow, f"_{register_as}")[MockEntity]) == 1


@pytest.mark.parametrize("register_as", ["new", "dirty", "deleted"])
def test_register_entity_from_entity(uow: UnitOfWork, register_as: str) -> None:
    test_entity = MockEntity(uow=uow, id_=1)

    getattr(test_entity, f"mark_{register_as}")()

    assert len(getattr(uow, f"_{register_as}")) == 1
    assert MockEntity in getattr(uow, f"_{register_as}")
    assert test_entity in getattr(uow, f"_{register_as}")[MockEntity]
    assert len(getattr(uow, f"_{register_as}")[MockEntity]) == 1


@pytest.mark.parametrize("register_as", ["new", "dirty", "deleted"])
def test_register_multiple_entities_of_same_type(uow: UnitOfWork, register_as: str) -> None:
    test_entity1 = MockEntity(uow=uow, id_=1)
    test_entity2 = MockEntity(uow=uow, id_=2)
    test_entity3 = MockEntity(uow=uow, id_=3)

    getattr(uow, f"register_{register_as}")(entity=test_entity1)
    getattr(uow, f"register_{register_as}")(entity=test_entity2)
    getattr(uow, f"register_{register_as}")(entity=test_entity3)

    assert len(getattr(uow, f"_{register_as}")) == 1
    assert MockEntity in getattr(uow, f"_{register_as}")
    assert test_entity1 in getattr(uow, f"_{register_as}")[MockEntity]
    assert test_entity2 in getattr(uow, f"_{register_as}")[MockEntity]
    assert test_entity3 in getattr(uow, f"_{register_as}")[MockEntity]
    assert len(getattr(uow, f"_{register_as}")[MockEntity]) == 3


@pytest.mark.parametrize(
    ("register_as", "called_method"),
    [("new", "add_all"), ("dirty", "update_all"), ("deleted", "delete_all")],
)
async def test_commit_entities(
    mock_connection: AsyncMock,
    mock_mapper: AsyncMock,
    uow: UnitOfWork,
    register_as: str,
    called_method: str,
) -> None:
    test_entity1 = MockEntity(uow=uow, id_=1)
    test_entity2 = MockEntity(uow=uow, id_=2)
    getattr(uow, f"register_{register_as}")(entity=test_entity1)
    getattr(uow, f"register_{register_as}")(entity=test_entity2)

    await uow.commit()

    getattr(mock_mapper, called_method).assert_called_once_with([test_entity1, test_entity2])
    getattr(mock_mapper, called_method).assert_awaited_once()
    mock_connection.transaction.assert_called_once()
