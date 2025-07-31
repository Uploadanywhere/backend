from asyncpg import Connection

from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.interfaces import AsyncDataMapper


class UserMapper(AsyncDataMapper[User, Connection]):
    def __init__(self, connection: Connection) -> None:
        self._con = connection

    async def add_all(self, users: list[User]) -> None:
        await self._con.executemany(
            """
                INSERT INTO users (user_id, username, password, email) VALUES ($1, $2, $3, $4);
            """,
            [(user.id, user.username, user.password, user.email) for user in users],
        )

    async def update_all(self, users: list[User]) -> None:
        await self._con.executemany(
            """
                UPDATE users SET username=$2, password=$3, email=$4
                WHERE user_id=$1;
            """,
            [(user.id, user.username, user.password, user.email) for user in users],
        )

    async def delete_all(self, users: list[User]) -> None:
        await self._con.executemany(
            """
                DELETE FROM users WHERE user_id = $1;
            """,
            [(user.id,) for user in users],
        )
