import typing as t
from dataclasses import dataclass

import pytest
from asyncpg import Connection
from uuid6 import UUID

from uploadanywhere.domain.entities.user import User


@dataclass
class UserFactory:
    __slots__ = ("con",)

    con: Connection

    async def fetch_user(self, id_: UUID | str | int) -> dict[str, t.Any]:
        sql = """
            SELECT *
            FROM users
            WHERE user_id = $1
        """
        result = await self.con.fetchrow(sql, id_)
        if result:
            return dict(result)
        return {}

    async def create_user(self, user: User) -> None:
        await self.con.execute(
            """
                INSERT INTO users (user_id, username, password, email) VALUES ($1, $2, $3, $4);
            """,
            user.id,
            user.username,
            user.password,
            user.email,
        )

    async def count(self) -> int:
        return await self.con.fetchval("SELECT COUNT(*) FROM users")


@pytest.fixture
def user_factory(con: Connection) -> UserFactory:
    return UserFactory(con)
