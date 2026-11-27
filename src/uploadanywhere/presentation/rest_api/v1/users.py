from dataclasses import dataclass

from dishka.integrations.litestar import FromDishka
from litestar import Controller, get, patch
from uuid6 import UUID

from uploadanywhere.application.command_processors.update_user_processor import UpdateUserCommand
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.identity_provider import IdentityProvider


@dataclass
class UserDataResponse:
    id: UUID


@dataclass
class UserUpdateRequest:
    username: str


class UsersController(Controller):
    path = "/users"

    @get(path="/me")
    async def me(self, idp: FromDishka[IdentityProvider]) -> UserDataResponse:
        user_id = await idp.get_current_user_id()
        return UserDataResponse(id=user_id)

    @patch("/me")
    async def update_user(
        self,
        data: UserUpdateRequest,
        update_user: FromDishka[CommandProcessor[UpdateUserCommand, None]],
    ) -> None:
        await update_user.process(UpdateUserCommand(username=data.username))
