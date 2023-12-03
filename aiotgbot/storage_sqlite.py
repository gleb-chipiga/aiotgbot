import json
from pathlib import Path
from typing import Any, AsyncIterator, Final, cast

import aiosqlite

from .helpers import Json, json_dumps
from .storage import StorageProtocol

__all__ = ("SQLiteStorage",)


class SQLiteStorage(StorageProtocol):
    def __init__(
        self,
        database: str | Path,
        **kwargs: Any,
    ) -> None:
        self._database: Final[str | Path] = database
        self._kwargs: Final[dict[str, Any]] = kwargs
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self._connection is not None:
            raise RuntimeError("Already connected")
        self._connection = await aiosqlite.connect(
            self._database,
            isolation_level=None,
            **self._kwargs,
        )
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS kv "
                "(key TEXT NOT NULL PRIMARY KEY, value TEXT NOT NULL)"
            )

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Not connected")
        return self._connection

    async def close(self) -> None:
        if self._connection is None:
            raise RuntimeError("Not connected")
        await self._connection.close()
        self._connection = None

    async def set(self, key: str, value: Json = None) -> None:
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
                (key, json_dumps(value)),
            )

    async def get(self, key: str) -> Json:
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT value FROM kv WHERE key = ?", (key,))
            row = await cursor.fetchone()
            if row is not None:
                return cast(Json, json.loads(row[0]))
            else:
                return None

    async def delete(self, key: str) -> None:
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM kv WHERE key = ?", (key,))

    async def iterate(
        self, prefix: str = ""
    ) -> AsyncIterator[tuple[str, Json]]:
        async with self.connection.execute(
            "SELECT key, value FROM kv WHERE key LIKE ? ORDER BY key",
            (f"{prefix}%",),
        ) as cursor:
            async for row in cursor:
                yield row[0], json.loads(row[1])

    async def clear(self) -> None:
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM kv")
            await self.connection.execute("VACUUM")

    def raw_connection(self) -> Any:
        return self.connection
