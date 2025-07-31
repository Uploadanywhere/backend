from uuid6 import uuid7

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.social_account import SocialAccount
from uploadanywhere.domain.entities.workspace import Workspace
from uploadanywhere.domain.identifiers import SocialAccountId


def test_delete_post(fake_uow_registrator: UoWRegistrator, workspace: Workspace) -> None:
    post = SocialAccount(
        uow=fake_uow_registrator,
        social_account_id=SocialAccountId(uuid7()),
        workspace_id=workspace.id,
        platform="example_platform",
        account_name="example_account",
        auth_data={},
    )

    post.delete()

    assert post in fake_uow_registrator._deleted[SocialAccount]


def test_create_post(fake_uow_registrator: UoWRegistrator, workspace: Workspace) -> None:
    post = SocialAccount.create(
        uow=fake_uow_registrator,
        social_account_id=SocialAccountId(uuid7()),
        workspace_id=workspace.id,
        platform="example_platform",
        account_name="example_account",
        auth_data={},
    )

    assert post in fake_uow_registrator._new[SocialAccount]
