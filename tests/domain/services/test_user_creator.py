import typing as t
from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import AsyncContainer
from uuid6 import uuid7

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.exceptions import AlreadyExistsError, ValidationError
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository
from uploadanywhere.domain.services import UserCreator

_user_id = UserId(uuid7())


class MockUserRepository(UserRepository):
    def __init__(self, unit_of_work: UoWRegistrator, connection: t.Any) -> None:
        self._uow = unit_of_work
        self._connection = connection

    _load = AsyncMock(return_value=None)
    with_id = AsyncMock(return_value=None)
    with_email = AsyncMock(return_value=None)
    with_username = AsyncMock(return_value=None)


@pytest.fixture
def repository_mock(fake_uow_registrator: UoWRegistrator) -> MockUserRepository:
    return MockUserRepository(unit_of_work=fake_uow_registrator, connection=MagicMock())


@pytest.fixture
def service(repository_mock: UserRepository, fake_uow_registrator: UoWRegistrator) -> UserCreator:
    return UserCreator(repository_mock, fake_uow_registrator)


async def test_user_creation(service: UserCreator, fake_uow_registrator: UoWRegistrator) -> None:
    got = await service(username="John Doe", password="password", email="john_doe@example.com", user_id=_user_id)

    assert got == User(
        uow=fake_uow_registrator,
        username="username=John Doe",
        email="john_doe@example.com",
        password="password",
        user_id=_user_id,
    )


async def test_new_user_marked_as_new(service: UserCreator, fake_uow_registrator: UoWRegistrator) -> None:
    got = await service(username="John Doe", password="password", email="john_doe@example.com", user_id=_user_id)

    assert fake_uow_registrator._new == {User: [got]}


async def test_service_raises_exception_for_empty_email(service: UserCreator) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Email cannot be empty"):
        await service(username="john_doe", password="password", email="", user_id=_user_id)


async def test_service_raises_exception_for_empty_password(service: UserCreator) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Password cannot be empty"):
        await service(username="john_doe", password="", email="john_doe@example.com", user_id=_user_id)


async def test_service_raises_exception_for_none_username(service: UserCreator) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        await service(username=None, password="password", email="john_doe@example.com", user_id=_user_id)  # type: ignore[arg-type]


async def test_service_raises_exception_for_none_password(service: UserCreator) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Password cannot be empty"):
        await service(username="john_doe", password=None, email="john_doe@example.com", user_id=_user_id)  # type: ignore[arg-type]


async def test_service_raises_exception_for_none_email(service: UserCreator) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Email cannot be empty"):
        await service(username="john_doe", password="password", email=None, user_id=_user_id)  # type: ignore[arg-type]


async def test_service_raises_exception_for_empty_username(service: UserCreator) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        await service("", "password", email="john_doe@example.com", user_id=_user_id)


async def test_service_raises_exception_for_duplicate_id(rs_container: AsyncContainer, db_user: User) -> None:
    repository = await rs_container.get(UserRepository)
    uow = await rs_container.get(UoWRegistrator)

    service = UserCreator(repository, uow)

    # Act & Assert
    with pytest.raises(AlreadyExistsError, match="User with the same ID already exists"):
        await service("John Second", "password", email="john_second@example.com", user_id=db_user.id)


async def test_service_raises_exception_for_duplicate_email(rs_container: AsyncContainer, db_user: User) -> None:
    repository = await rs_container.get(UserRepository)
    uow = await rs_container.get(UoWRegistrator)

    service = UserCreator(repository, uow)

    # Act & Assert
    with pytest.raises(AlreadyExistsError, match="User with the same email already exists"):
        await service("John Second", "password", email=db_user.email, user_id=_user_id)


async def test_service_raises_exception_for_duplicate_username(rs_container: AsyncContainer, db_user: User) -> None:
    repository = await rs_container.get(UserRepository)
    uow = await rs_container.get(UoWRegistrator)

    service = UserCreator(repository, uow)

    # Act & Assert
    with pytest.raises(AlreadyExistsError, match="User with the same username already exists"):
        await service(db_user.username, "password", email="john_second@example.com", user_id=_user_id)
