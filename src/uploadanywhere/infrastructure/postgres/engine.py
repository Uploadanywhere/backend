__all__ = ("Engine",)

import typing as t
from types import TracebackType

from asyncpg import create_pool
from asyncpg.pool import Pool, PoolConnectionProxy


class Engine:
    __slots__ = "_global_con", "_pool", "_use_single_con"

    _pool: Pool
    _use_single_con: bool
    _global_con: PoolConnectionProxy | None

    def __init__(self, pool: Pool, use_single_connection: bool) -> None:
        self._pool = pool
        self._use_single_con = use_single_connection

        self._global_con = None

    @classmethod
    async def create(
        cls,
        url: str,
        *,
        use_single_connection: bool = False,
        **kwargs: t.Any,
    ) -> Engine:
        pool = await create_pool(url, min_size=2, init=cls._set_codecs, **kwargs)  # type: ignore[call-overload]
        return cls(pool, use_single_connection)

    async def close(self) -> None:
        await self._pool.close()

    def acquire(self) -> ConnectionAcquire:
        return ConnectionAcquire(self)

    async def _acquire(self) -> PoolConnectionProxy:
        if self._use_single_con:
            self._global_con = self._global_con or await self._pool.acquire()
            return self._global_con

        return await self._pool.acquire()

    async def release(self, con: PoolConnectionProxy, *, force: bool = False) -> None:
        if not self._use_single_con or force:
            await self._pool.release(con)
            self._global_con = None

    async def healthcheck(self) -> None:
        async with self.acquire() as con:
            await con.execute("SELECT 1")

    @staticmethod
    async def _set_codecs(con: PoolConnectionProxy) -> None:
        """Override this method if you want to set custom codecs."""


class ConnectionAcquire:
    __slots__ = "con", "engine"

    engine: Engine
    con: PoolConnectionProxy

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    async def __call__(self) -> PoolConnectionProxy:
        self.con = await self.engine._acquire()  # ruff: ignore[private-member-access]
        return self.con

    def __await__(self) -> t.Generator[t.Any, None, PoolConnectionProxy]:
        return self().__await__()

    async def __aenter__(self) -> PoolConnectionProxy:
        return await self()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tv: TracebackType | None,
    ) -> None:
        await self.engine.release(self.con)
