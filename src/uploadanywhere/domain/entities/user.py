import typing as t

from uploadanywhere.domain.entities.base import Entity, UoWRegistrator
from uploadanywhere.domain.exceptions import ValidationError
from uploadanywhere.domain.identifiers import UserId


def validate_username(username: str) -> None:
    if not username:
        raise ValidationError("Username cannot be empty")


class User(Entity[UserId]):
    id: UserId
    username: str
    password: str
    email: str

    def __init__(self, uow: UoWRegistrator, user_id: UserId, username: str, password: str, email: str) -> None:
        super().__init__(uow=uow)
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def create(cls, uow: UoWRegistrator, user_id: UserId, username: str, password: str, email: str) -> t.Self:
        user = cls(uow=uow, user_id=user_id, username=username, password=password, email=email)
        user.mark_new()
        return user

    def change_username(self, new_username: str) -> None:
        validate_username(new_username)
        self.username = new_username
        self.mark_dirty()
