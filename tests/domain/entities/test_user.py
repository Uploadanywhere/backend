import pytest
from uuid6 import uuid7

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.exceptions import ValidationError
from uploadanywhere.domain.identifiers import UserId


def test_delete_user(fake_uow_registrator: UoWRegistrator) -> None:
    user = User(
        uow=fake_uow_registrator,
        user_id=UserId(uuid7()),
        username="John Doe",
        password="password",
        email="john_doe@example.com",
    )

    user.delete()

    assert user in fake_uow_registrator._deleted[User]


def test_create_user(fake_uow_registrator: UoWRegistrator) -> None:
    user = User.create(
        uow=fake_uow_registrator,
        user_id=UserId(uuid7()),
        username="John Doe",
        password="password",
        email="john_doe@example.com",
    )

    assert user in fake_uow_registrator._new[User]


def test_user_str_representation(user: User) -> None:
    assert str(user) == f"User(id={user.id})"


def test_user_repr_representation(user: User) -> None:
    assert repr(user) == f"User(id={user.id})"


def test_change_username(user: User) -> None:
    user.change_username("Jane Doe")

    assert user.username == "Jane Doe"


def test_change_username_raises_exception_for_empty_username(user: User) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        user.change_username("")


def test_change_username_raises_exception_for_none_username(user: User) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        user.change_username(None)  # type: ignore[arg-type]
