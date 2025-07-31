import typing as t
from dataclasses import dataclass

import pytest
from asyncpg import Connection
from uuid6 import UUID

from uploadanywhere.domain.entities.workspace import Workspace


@dataclass
class WorkspaceFactory:
    __slots__ = ("con",)

    con: Connection

    async def fetch_workspace(self, id_: UUID | str | int) -> dict[str, t.Any]:
        sql = """
            SELECT *
            FROM workspaces
            WHERE workspace_id = $1
        """
        result = await self.con.fetchrow(sql, id_)
        if result:
            return dict(result)
        return {}

    async def create_workspace(self, workspace: Workspace) -> None:
        await self.con.execute(
            """
                INSERT INTO workspaces (workspace_id, name, owner) VALUES ($1, $2, $3);
            """,
            workspace.id,
            workspace.name,
            workspace.owner_id,
        )

    async def count(self) -> int:
        return await self.con.fetchval("SELECT COUNT(*) FROM workspaces")


@pytest.fixture
def workspace_factory(con: Connection) -> WorkspaceFactory:
    return WorkspaceFactory(con)
