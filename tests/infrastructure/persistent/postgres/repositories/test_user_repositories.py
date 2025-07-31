import pytest
from dishka import AsyncContainer
from uuid6 import uuid7

from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository


@pytest.fixture
async def user_repository(rs_container: AsyncContainer) -> UserRepository:
    return await rs_container.get(UserRepository)


async def test_fetch_user_with_id(user_repository: UserRepository, db_user: User) -> None:
    got = await user_repository.with_id(db_user.id)

    assert got == db_user


async def test_fetch_user_with_id_if_user_not_found(user_repository: UserRepository, user: User) -> None:
    got = await user_repository.with_id(user.id)  # User not found because it doesn't save in the database

    assert got is None


@pytest.mark.usefixtures("db_user")
async def test_fetch_user_with_id_when_id_is_wrong(user_repository: UserRepository) -> None:
    got = await user_repository.with_id(UserId(uuid7()))

    assert got is None


async def test_fetch_user_with_username(user_repository: UserRepository, db_user: User) -> None:
    got = await user_repository.with_username(db_user.username)

    assert got == db_user


async def test_fetch_user_with_username_if_user_not_found(user_repository: UserRepository, user: User) -> None:
    got = await user_repository.with_username(user.username)  # User not found because it doesn't save in the database

    assert got is None


async def test_fetch_user_with_username_when_username_is_wrong(user_repository: UserRepository, db_user: User) -> None:
    got = await user_repository.with_username(f"{db_user.username}_wrong")

    assert got is None


async def test_fetch_user_with_email(user_repository: UserRepository, db_user: User) -> None:
    got = await user_repository.with_email(db_user.email)

    assert got == db_user


async def test_fetch_user_with_email_if_user_not_found(user_repository: UserRepository, user: User) -> None:
    got = await user_repository.with_email(user.email)  # User not found because it doesn't save in the database

    assert got is None


async def test_fetch_user_with_email_when_email_is_wrong(user_repository: UserRepository, db_user: User) -> None:
    got = await user_repository.with_email(f"{db_user.email}_wrong")

    assert got is None
