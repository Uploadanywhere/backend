from asyncpg import Connection

from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.entities.base import Entity
from uploadanywhere.domain.interfaces import Registry


class UnitOfWork(AsyncUoW[Connection, Entity]):
    def __init__(self, registry: Registry, connection: Connection) -> None:
        self._new = {}
        self._dirty = {}
        self._deleted = {}

        self._registry = registry
        self._connection = connection

    def register_new(self, *, entity: Entity) -> None:
        self._new.setdefault(type(entity), []).append(entity)

    def register_dirty(self, *, entity: Entity) -> None:
        self._dirty.setdefault(type(entity), []).append(entity)

    def register_deleted(self, *, entity: Entity) -> None:
        self._deleted.setdefault(type(entity), []).append(entity)

    async def commit(self) -> None:
        async with self._connection.transaction():
            sorted_mappers = self._registry.resolve_dependencies()
            for entry in sorted_mappers:
                for entity_type, mapper in entry.items():
                    new_objects = self._new.get(entity_type, [])
                    if new_objects:
                        await mapper.add_all(new_objects)

                    updated_objects = self._dirty.get(entity_type, [])
                    if updated_objects:
                        await mapper.update_all(updated_objects)

                    deleted_objects = self._deleted.get(entity_type, [])
                    if deleted_objects:
                        await mapper.delete_all(deleted_objects)
        self._new.clear()
        self._dirty.clear()
        self._deleted.clear()
