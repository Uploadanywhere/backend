from uuid6 import uuid7

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.entities.workspace import Workspace
from uploadanywhere.domain.identifiers import WorkspaceId


def test_delete_workspace(fake_uow_registrator: UoWRegistrator, user: User) -> None:
    workspace = Workspace(
        uow=fake_uow_registrator,
        workspace_id=WorkspaceId(uuid7()),
        name="Test Workspace",
        owner_id=user.id,
    )

    workspace.delete()

    assert workspace in fake_uow_registrator._deleted[Workspace]


def test_create_workspace(fake_uow_registrator: UoWRegistrator, user: User) -> None:
    workspace = Workspace.create(
        uow=fake_uow_registrator,
        workspace_id=WorkspaceId(uuid7()),
        name="Test Workspace",
        owner_id=user.id,
    )

    assert workspace in fake_uow_registrator._new[Workspace]
