from uuid6 import uuid7

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.post import Post, PostType
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.entities.workspace import Workspace
from uploadanywhere.domain.identifiers import PostId


def test_delete_post(fake_uow_registrator: UoWRegistrator, user: User, workspace: Workspace) -> None:
    post = Post(
        uow=fake_uow_registrator,
        post_id=PostId(uuid7()),
        workspace_id=workspace.id,
        author_id=user.id,
        post_type=PostType.TEXT,
    )

    post.delete()

    assert post in fake_uow_registrator._deleted[Post]


def test_create_post(fake_uow_registrator: UoWRegistrator, user: User, workspace: Workspace) -> None:
    post = Post.create(
        uow=fake_uow_registrator,
        post_id=PostId(uuid7()),
        workspace_id=workspace.id,
        author_id=user.id,
        post_type=PostType.TEXT,
    )

    assert post in fake_uow_registrator._new[Post]
