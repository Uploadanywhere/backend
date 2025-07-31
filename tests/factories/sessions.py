import typing as t
from dataclasses import dataclass

import pytest
from asyncpg import Connection, Record
from uuid6 import UUID

from uploadanywhere.domain.entities.session import Session


@dataclass
class SessionFactory:
    __slots__ = ("con",)

    con: Connection

    async def create_session(self, session: Session) -> None:
        await self.con.execute(
            """
                INSERT INTO sessions (session_id, user_id, expires_at) VALUES ($1, $2, $3);
            """,
            session.id,
            session.user_id,
            session.expires_at,
        )

    async def fetch_session(self, id_: str | UUID) -> dict[str, t.Any]:
        sql = "SELECT * FROM sessions WHERE session_id = $1"
        result = await self.con.fetchrow(sql, id_)
        if result:
            return dict(result)
        return {}

    async def get_latest_session(self) -> Record | None:
        return await self.con.fetchrow("SELECT session_id, expires_at FROM sessions ORDER BY session_id DESC LIMIT 1")

    async def count_sessions(self) -> int:
        return await self.con.fetchval("SELECT COUNT(*) FROM sessions")


@pytest.fixture
def session_factory(con: Connection) -> SessionFactory:
    return SessionFactory(con)
