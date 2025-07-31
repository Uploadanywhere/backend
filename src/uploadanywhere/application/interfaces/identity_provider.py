import typing as t

from uploadanywhere.domain.identifiers import UserId


class IdentityProvider(t.Protocol):
    async def get_current_user_id(self) -> UserId: ...
