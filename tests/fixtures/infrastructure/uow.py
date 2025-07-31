import pytest
from dishka import AsyncContainer

from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.entities.base import Entity, UoWRegistrator


class MockUowRegistrator(UoWRegistrator):
    def __init__(self) -> None:
        self._new = {}
        self._dirty = {}
        self._deleted = {}

    def register_new(self, entity: Entity) -> None:
        self._new.setdefault(type(entity), []).append(entity)

    def register_dirty(self, entity: Entity) -> None:
        self._dirty.setdefault(type(entity), []).append(entity)

    def register_deleted(self, entity: Entity) -> None:
        self._deleted.setdefault(type(entity), []).append(entity)


@pytest.fixture
def fake_uow_registrator() -> MockUowRegistrator:
    return MockUowRegistrator()


@pytest.fixture
async def uow(rs_container: AsyncContainer) -> AsyncUoW:
    return await rs_container.get(AsyncUoW)
