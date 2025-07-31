from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.user import User, validate_username
from uploadanywhere.domain.exceptions import AlreadyExistsError, ValidationError
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository


class UserCreator:
    def __init__(self, repository: UserRepository, uow: UoWRegistrator) -> None:
        self.repository = repository
        self.uow = uow

    async def __call__(self, username: str, password: str, email: str, user_id: UserId) -> User:
        validate_username(username)
        if not password:
            raise ValidationError("Password cannot be empty")
        if not email:
            raise ValidationError("Email cannot be empty")

        if await self.repository.with_email(email):
            raise AlreadyExistsError("User with the same email already exists")
        if await self.repository.with_username(username):
            raise AlreadyExistsError("User with the same username already exists")
        if await self.repository.with_id(user_id):
            raise AlreadyExistsError("User with the same ID already exists")

        return User.create(self.uow, user_id, username, password, email)
