import pytest

from uploadanywhere.domain.entities.base import Entity, UoWRegistrator


def test_delete_entity(fake_uow_registrator: UoWRegistrator) -> None:
    entity: Entity = Entity(uow=fake_uow_registrator)

    entity.delete()

    assert entity in fake_uow_registrator._deleted[Entity]


@pytest.mark.parametrize(
    "register_as",
    ["new", "dirty", "deleted"],
    ids=["register_as_new", "register_as_dirty", "register_as_deleted"],
)
def test_mark_entity_as_(fake_uow_registrator: UoWRegistrator, register_as: str) -> None:
    entity: Entity = Entity(uow=fake_uow_registrator)

    getattr(entity, f"mark_{register_as}")()

    assert entity in getattr(fake_uow_registrator, f"_{register_as}")[Entity]


def test_entity_str_representation(fake_uow_registrator: UoWRegistrator) -> None:
    entity: Entity = Entity(uow=fake_uow_registrator)

    entity.id = 77

    assert str(entity) == "Entity(id=77)"


def test_entity_repr_representation(fake_uow_registrator: UoWRegistrator) -> None:
    entity: Entity = Entity(uow=fake_uow_registrator)

    entity.id = 77

    assert repr(entity) == "Entity(id=77)"


def test_entity_hash(fake_uow_registrator: UoWRegistrator) -> None:
    entity: Entity = Entity(uow=fake_uow_registrator)

    entity.id = 77

    assert hash(entity) == 77
