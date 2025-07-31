from dataclasses import dataclass

from uploadanywhere.application.command_processors.transaction_processor import TransactionProcessor
from uploadanywhere.application.exceptions import NotAuthenticatedError
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.identity_provider import IdentityProvider
from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.interfaces.user_repository import UserRepository


@dataclass
class UpdateUserCommand:
    username: str


class UpdateUserProcessor(CommandProcessor[UpdateUserCommand, None]):
    def __init__(
        self,
        user_repository: UserRepository,
        idp: IdentityProvider,
    ) -> None:
        self._user_repository = user_repository
        self._idp = idp

    async def process(self, command: UpdateUserCommand) -> None:
        user_id = await self._idp.get_current_user_id()
        user = await self._user_repository.with_id(user_id)
        if not user:
            raise NotAuthenticatedError("User not found")

        field_method_mapping = {
            "username": user.change_username,
        }

        for field in command.__dict__:
            if field in field_method_mapping:
                method = field_method_mapping[field]
                method(getattr(command, field))


class UpdateUserFactory:
    @classmethod
    def execute(
        cls,
        *,
        user_repository: UserRepository,
        idp: IdentityProvider,
        uow: AsyncUoW,
    ) -> CommandProcessor[UpdateUserCommand, None]:
        update_user_processor = UpdateUserProcessor(user_repository, idp)
        return TransactionProcessor(uow=uow, processor=update_user_processor)
