from asyncpg import Connection, Record

from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository


class UserRepositoryImpl(UserRepository[Connection, Record]):
    def __init__(self, connection: Connection, unit_of_work: UoWRegistrator) -> None:
        self._connection = connection
        self._unit_of_work = unit_of_work

    def _load(self, result: Record) -> User:
        return User(
            uow=self._unit_of_work,
            user_id=result["user_id"],
            username=result["username"],
            email=result["email"],
            password=result["password"],
        )

    async def with_id(self, entity_id: UserId) -> User | None:
        stmt = "SELECT * FROM users WHERE user_id = $1"
        result = await self._connection.fetchrow(stmt, entity_id)
        if result:
            return self._load(result)
        return None

    async def with_email(self, email: str) -> User | None:
        stmt = "SELECT * FROM users WHERE email = $1"
        result = await self._connection.fetchrow(stmt, email)
        if result:
            return self._load(result)
        return None

    async def with_username(self, username: str) -> User | None:
        stmt = "SELECT * FROM users WHERE username = $1"
        result = await self._connection.fetchrow(stmt, username)
        if result:
            return self._load(result)
        return None
