import typing as t

from uploadanywhere.domain.entities.base import Entity, UoWRegistrator
from uploadanywhere.domain.identifiers import SocialAccountId, WorkspaceId


class SocialAccount(Entity):
    def __init__(
        self,
        uow: UoWRegistrator,
        social_account_id: SocialAccountId,
        workspace_id: WorkspaceId,
        platform: str,
        account_name: str,
        auth_data: dict,
    ) -> None:
        super().__init__(uow=uow)
        self.social_account_id = social_account_id
        self.workspace_id = workspace_id
        self.platform = platform
        self.account_name = account_name
        self.auth_data = auth_data

    @classmethod
    def create(
        cls,
        uow: UoWRegistrator,
        social_account_id: SocialAccountId,
        workspace_id: WorkspaceId,
        platform: str,
        account_name: str,
        auth_data: dict,
    ) -> t.Self:
        instance = cls(uow, social_account_id, workspace_id, platform, account_name, auth_data)
        instance.mark_new()
        return instance
