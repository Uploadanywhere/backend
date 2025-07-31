import typing as t

from uploadanywhere.domain.entities.base import Entity, UoWRegistrator
from uploadanywhere.domain.identifiers import SocialAccountId, UserId, WorkspaceId


class Workspace(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        workspace_id: WorkspaceId,
        name: str,
        owner_id: UserId,
        members: list[UserId] | None = None,
        social_accounts: list[SocialAccountId] | None = None,
    ) -> None:
        super().__init__(uow=uow)
        self.id = workspace_id
        self.name = name
        self.owner_id = owner_id
        self.members = members or []
        self.social_accounts = social_accounts or []

    @classmethod
    def create(cls, uow: UoWRegistrator, workspace_id: WorkspaceId, name: str, owner_id: UserId) -> t.Self:
        instance = cls(uow, workspace_id, name, owner_id)
        instance.mark_new()
        return instance
