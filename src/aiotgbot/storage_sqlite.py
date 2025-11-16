import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Final, TypedDict, Unpack, cast

import aiosqlite
from typing_extensions import override  # Python 3.11 compatibility

from .helpers import Json, json_dumps
from .storage import StorageProtocol

__all__ = ("SQLiteStorage",)


class _ConnectKwargs(TypedDict, total=False):
    timeout: float
    detect_types: int
    check_same_thread: bool
    factory: type[aiosqlite.Connection]
    cached_statements: int
    uri: bool
    loop: asyncio.AbstractEventLoop | None
    iter_chunk_size: int


class SQLiteStorage(StorageProtocol):
    def __init__(
        self,
        database: str | Path,
        *,
        isolation_level: str | None = None,
        **kwargs: Unpack[_ConnectKwargs],
    ) -> None:
        self._database: Final[str | Path] = database
        self._isolation_level: Final[str | None] = isolation_level
        self._kwargs: Final[_ConnectKwargs] = kwargs
        self._connection: aiosqlite.Connection | None = None

    @override
    async def connect(self) -> None:
        if self._connection is not None:
            raise RuntimeError("Already connected")
        connection = await aiosqlite.connect(
            self._database,
            isolation_level=self._isolation_level,
            **self._kwargs,
        )
        self._connection = connection
        async with connection.cursor() as cursor:
            query = (
                "CREATE TABLE IF NOT EXISTS kv "
                + "(key TEXT NOT NULL PRIMARY KEY, value TEXT NOT NULL)"
            )
            _ = await cursor.execute(query)

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Not connected")
        return self._connection

    @override
    async def close(self) -> None:
        if self._connection is None:
            raise RuntimeError("Not connected")
        await self._connection.close()
        self._connection = None

    @override
    async def set(self, key: str, value: Json | None = None) -> None:
        async with self.connection.cursor() as cursor:
            _ = await cursor.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
                (key, json_dumps(value)),
            )

    @override
    async def get(self, key: str) -> Json:
        async with self.connection.cursor() as cursor:
            _ = await cursor.execute("SELECT value FROM kv WHERE key = ?", (key,))
            row = await cursor.fetchone()
            if row is not None:
                value_str = cast(str, row[0])
                return cast(Json, json.loads(value_str))
            return None

    @override
    async def delete(self, key: str) -> None:
        async with self.connection.cursor() as cursor:
            _ = await cursor.execute("DELETE FROM kv WHERE key = ?", (key,))

    @override
    async def iterate(self, prefix: str = "") -> AsyncIterator[tuple[str, Json]]:
        async with self.connection.execute(
            "SELECT key, value FROM kv WHERE key LIKE ? ORDER BY key",
            (f"{prefix}%",),
        ) as cursor:
            async for row in cursor:
                key = cast(str, row[0])
                raw_value = cast(str, row[1])
                yield key, cast(Json, json.loads(raw_value))

    @override
    async def clear(self) -> None:
        async with self.connection.cursor() as cursor:
            _ = await cursor.execute("DELETE FROM kv")
            _ = await self.connection.execute("VACUUM")

    @override
    def raw_connection(self) -> aiosqlite.Connection:
        return self.connection
