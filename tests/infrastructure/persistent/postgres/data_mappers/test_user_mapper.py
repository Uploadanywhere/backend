import pytest
from asyncpg import Connection
from dishka import AsyncContainer
from uuid6 import UUID

from tests.factories.users import UserFactory
from uploadanywhere.domain.entities.user import User
from uploadanywhere.infrastructure.postgres.data_mappers import UserMapper


@pytest.fixture
async def user_mapper(rs_container: AsyncContainer) -> UserMapper:
    con = await rs_container.get(Connection)
    return UserMapper(connection=con)


async def test_user_mapper_create_all(user_mapper: UserMapper, user: User, user_factory: UserFactory) -> None:
    await user_mapper.add_all([user])

    assert await user_factory.fetch_user(user.id) == {
        "email": user.email,
        "password": user.password,
        "user_id": UUID(str(user.id)),
        "username": user.username,
    }


async def test_user_mapper_update_all(user_mapper: UserMapper, db_user: User, user_factory: UserFactory) -> None:
    db_user.email = "new_email@example.com"

    await user_mapper.update_all([db_user])

    assert await user_factory.fetch_user(db_user.id) == {
        "email": "new_email@example.com",
        "password": db_user.password,
        "user_id": UUID(str(db_user.id)),
        "username": db_user.username,
    }


async def test_user_mapper_delete_all(user_mapper: UserMapper, db_user: User, user_factory: UserFactory) -> None:
    await user_mapper.delete_all([db_user])

    assert not await user_factory.fetch_user(db_user.id)
    assert await user_factory.count() == 0
