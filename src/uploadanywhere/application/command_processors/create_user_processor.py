from dataclasses import dataclass

from uuid6 import UUID

from uploadanywhere.application.command_processors.transaction_processor import TransactionProcessor
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.id_generator import IDGenerator
from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.services import UserCreator


@dataclass
class CreateUserCommand:
    username: str
    email: str
    password: str


class CreateUserProcessor(CommandProcessor[CreateUserCommand, UserId]):
    def __init__(
        self,
        id_generator: IDGenerator[UUID],
        password_hasher: PasswordHasher,
        create_user: UserCreator,
    ) -> None:
        self._id_generator = id_generator
        self._password_hasher = password_hasher
        self._create_user = create_user

    async def process(self, command: CreateUserCommand) -> UserId:
        hashed_password = self._password_hasher.encode(command.password)
        user = await self._create_user(
            username=command.username,
            email=command.email,
            password=hashed_password,
            user_id=UserId(self._id_generator()),
        )
        return user.id


class CreateUserFactory:
    @classmethod
    def execute(
        cls,
        *,
        id_generator: IDGenerator[UUID],
        password_hasher: PasswordHasher,
        create_user: UserCreator,
        uow: AsyncUoW,
    ) -> CommandProcessor[CreateUserCommand, UserId]:
        create_user_processor = CreateUserProcessor(id_generator, password_hasher, create_user)
        return TransactionProcessor(uow=uow, processor=create_user_processor)
