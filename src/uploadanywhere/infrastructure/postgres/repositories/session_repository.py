from datetime import UTC, datetime

from asyncpg import Connection, Record

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.identifiers import SessionId
from uploadanywhere.domain.interfaces.session_repository import SessionRepository


class SessionRepositoryImpl(SessionRepository):
    def __init__(self, connection: Connection, unit_of_work: UoWRegistrator) -> None:
        self._connection = connection
        self._unit_of_work = unit_of_work

    def _load(self, result: Record) -> Session:
        return Session(
            uow=self._unit_of_work,
            session_id=result["session_id"],
            user_id=result["user_id"],
            expires_at=result["expires_at"],
        )

    async def with_id(self, entity_id: SessionId) -> Session | None:
        stmt = "SELECT * FROM sessions WHERE session_id = $1"
        result = await self._connection.fetchrow(stmt, entity_id)
        if result:
            return self._load(result)
        return None

    async def active_with_id(self, entity_id: SessionId) -> Session | None:
        stmt = "SELECT * FROM sessions WHERE session_id = $1 and expires_at > $2"
        result = await self._connection.fetchrow(stmt, entity_id, datetime.now(UTC))
        if result:
            return self._load(result)
        return None
