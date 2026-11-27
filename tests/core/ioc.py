from asyncpg import Connection
from dishka import Scope, provide

from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.infrastructure.hashers.md5_hasher import MD5PasswordHasher
from uploadanywhere.infrastructure.postgres.engine import Engine
from uploadanywhere.main.ioc import AppProvider


class FakeAppProvider(AppProvider):
    def __init__(self, db: Engine, con: Connection) -> None:
        super().__init__()
        self.db = db
        self.con = con

    @provide(scope=Scope.APP)
    def get_asyncpg_engine(self) -> Engine:
        return self.db

    @provide(scope=Scope.REQUEST)
    def get_connection(self) -> Connection:
        return self.con

    password_hasher = provide(MD5PasswordHasher, scope=Scope.APP, provides=PasswordHasher)
