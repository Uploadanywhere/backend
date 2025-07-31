from asyncpg import Connection

from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.interfaces import AsyncDataMapper


class SessionMapper(AsyncDataMapper[Session, Connection]):
    def __init__(self, connection: Connection) -> None:
        self._con = connection

    async def add_all(self, sessions: list[Session]) -> None:
        await self._con.executemany(
            """
                INSERT INTO sessions (session_id, user_id, expires_at) VALUES ($1, $2, $3);
            """,
            [(session.id, session.user_id, session.expires_at) for session in sessions],
        )

    async def update_all(self, sessions: list[Session]) -> None:
        await self._con.executemany(
            """
                UPDATE sessions SET expires_at=$2
                WHERE session_id=$1;
            """,
            [(session.id, session.expires_at) for session in sessions],
        )

    async def delete_all(self, sessions: list[Session]) -> None:
        await self._con.executemany(
            """
                DELETE FROM sessions WHERE session_id = $1;
            """,
            [(session.id,) for session in sessions],
        )
