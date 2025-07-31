import typing as t
from enum import Enum

from uploadanywhere.domain.entities.base import Entity, UoWRegistrator
from uploadanywhere.domain.identifiers import PostId, UserId, WorkspaceId


class PostType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    SHORT_VIDEO = "short_video"
    LINK = "link"


class Post(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        post_id: PostId,
        workspace_id: WorkspaceId,
        author_id: UserId,
        post_type: PostType,
    ) -> None:
        super().__init__(uow=uow)
        self.post_id = post_id
        self.workspace_id = workspace_id
        self.author_id = author_id
        self.post_type = post_type

    @classmethod
    def create(
        cls,
        uow: UoWRegistrator,
        post_id: PostId,
        workspace_id: WorkspaceId,
        author_id: UserId,
        post_type: PostType,
    ) -> t.Self:
        instance = cls(uow, post_id, workspace_id, author_id, post_type)
        instance.mark_new()
        return instance


class PostVideo(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        post_id: PostId,
        video_url: str,
        thumbnail_url: str,
        tags: list[str],
        title: str,
        description: str,
    ) -> None:
        super().__init__(uow=uow)
        self.post_id = post_id
        self.video_url = video_url
        self.thumbnail_url = thumbnail_url
        self.tags = tags
        self.title = title
        self.description = description

    @classmethod
    def create(
        cls,
        uow: UoWRegistrator,
        post_id: PostId,
        video_url: str,
        thumbnail_url: str,
        tags: list[str],
        title: str,
        description: str,
    ) -> t.Self:
        instance = cls(uow, post_id, video_url, thumbnail_url, tags, title, description)
        instance.mark_new()
        return instance


class PostShorts(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        post_id: PostId,
        video_url: str,
        thumbnail_url: str,
        tags: list[str],
        title: str,
        description: str,
    ) -> None:
        super().__init__(uow=uow)
        self.post_id = post_id
        self.video_url = video_url
        self.thumbnail_url = thumbnail_url
        self.tags = tags
        self.title = title
        self.description = description

    @classmethod
    def create(
        cls,
        uow: UoWRegistrator,
        post_id: PostId,
        video_url: str,
        thumbnail_url: str,
        tags: list[str],
        title: str,
        description: str,
    ) -> t.Self:
        instance = cls(uow, post_id, video_url, thumbnail_url, tags, title, description)
        instance.mark_new()
        return instance


class PostText(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        post_id: PostId,
        text: str,
    ) -> None:
        super().__init__(uow=uow)
        self.post_id = post_id
        self.text = text

    @classmethod
    def create(
        cls,
        uow: UoWRegistrator,
        post_id: PostId,
        text: str,
    ) -> t.Self:
        instance = cls(uow, post_id, text)
        instance.mark_new()
        return instance


class PostImage(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        post_id: PostId,
        image_url: str,
    ) -> None:
        super().__init__(uow=uow)
        self.post_id = post_id
        self.image_url = image_url

    @classmethod
    def create(
        cls,
        uow: UoWRegistrator,
        post_id: PostId,
        image_url: str,
    ) -> t.Self:
        instance = cls(uow, post_id, image_url)
        instance.mark_new()
        return instance
