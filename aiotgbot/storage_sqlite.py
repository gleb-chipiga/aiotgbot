import asyncio
import json
from enum import Enum
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple, Union

import aiosqlite

from .storage import BaseStorage
from .utils import json_dumps

JsonType = Union[int, float, str, bool, Dict, List]


class IsolationLevel(str, Enum):
    DEFERRED = 'DEFERRED'
    IMMEDIATE = 'IMMEDIATE'
    EXCLUSIVE = 'EXCLUSIVE'


class SQLiteStorage(BaseStorage):

    def __init__(self, database: Union[str, Path],
                 isolation_level: Optional[IsolationLevel] = None,
                 **kwargs) -> None:
        self._database: Final[Union[str, Path]] = database
        self._isolation_level: Final = isolation_level
        self._kwargs: Final = kwargs

        self._connection_lock: Optional[asyncio.Lock] = None
        self._connection: Optional[aiosqlite.Connection] = None

    async def connection(self) -> aiosqlite.Connection:
        if self._connection_lock is None:
            self._connection_lock = asyncio.Lock()

        async with self._connection_lock:
            if self._connection is None:
                self._connection = await aiosqlite.connect(
                    self._database,
                    isolation_level=(self._isolation_level.value
                                     if self._isolation_level is not None
                                     else None),
                    **self._kwargs
                )
                async with self._connection.cursor() as cursor:
                    await cursor.execute('CREATE TABLE IF NOT EXISTS kv'
                                         '(key TEXT PRIMARY KEY, value TEXT)')

        return self._connection

    async def close(self) -> None:
        if self._connection_lock is not None:
            async with self._connection_lock:
                if self._connection is not None:
                    await self._connection.close()
                    self._connection = None

    async def set(self, key: str, value: Optional[JsonType] = None) -> None:
        connection = await self.connection()
        async with connection.cursor() as cursor:
            await cursor.execute(
                'INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)',
                (key, json_dumps(value)))

    async def get(self, key: str) -> Optional[JsonType]:
        connection = await self.connection()
        async with connection.cursor() as cursor:
            await cursor.execute('SELECT value FROM kv WHERE key = ?', (key,))
            row = await cursor.fetchone()
            if row is not None:
                return json.loads(row[0])
            else:
                return None

    async def delete(self, key: str) -> None:
        connection = await self.connection()
        async with connection.cursor() as cursor:
            await cursor.execute('DELETE FROM kv WHERE key = ?', (key,))

    async def keys(self, prefix: str) -> Tuple[str, ...]:
        connection = await self.connection()
        async with connection.cursor() as cursor:
            await cursor.execute(
                'SELECT key FROM kv WHERE key LIKE ? ORDER BY key',
                (f'{prefix}%',))
            return tuple(row[0] for row in await cursor.fetchall())

    async def reset_all(self) -> None:
        connection = await self.connection()
        async with connection.cursor() as cursor:
            await cursor.execute('DELETE FROM kv')
            await cursor.execute('VACUUM')
