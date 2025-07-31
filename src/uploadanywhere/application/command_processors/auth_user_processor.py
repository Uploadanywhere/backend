from dataclasses import dataclass

from uuid6 import UUID

from uploadanywhere.application.exceptions import NotAuthenticatedError
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.id_generator import IDGenerator
from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository


@dataclass
class AuthUserCommand:
    username: str
    password: str


class AuthUserProcessor(CommandProcessor[AuthUserCommand, UserId]):
    def __init__(
        self,
        id_generator: IDGenerator[UUID],
        password_hasher: PasswordHasher,
        user_repository: UserRepository,
    ) -> None:
        self._id_generator = id_generator
        self._password_hasher = password_hasher
        self._user_repository = user_repository

    async def process(self, command: AuthUserCommand) -> UserId:
        user = await self._user_repository.with_username(command.username)
        if not user or not self._password_hasher.verify(command.password, user.password):
            raise NotAuthenticatedError("Invalid username or password")
        return user.id
