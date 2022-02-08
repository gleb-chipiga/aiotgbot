from pathlib import Path

import aiosqlite
import pytest

from aiotgbot import StorageProtocol
from aiotgbot.storage_sqlite import SQLiteStorage


def test_storage_protocol(tmpdir: Path) -> None:
    storage: StorageProtocol = SQLiteStorage(tmpdir / 'test.sqlite')
    assert isinstance(storage, StorageProtocol)


@pytest.mark.asyncio
async def test_sqlite_storage(tmpdir: Path) -> None:
    storage: StorageProtocol = SQLiteStorage(tmpdir / 'test.sqlite')
    with pytest.raises(RuntimeError, match='Not connected'):
        await storage.set('key1', 'value1')
    with pytest.raises(RuntimeError, match='Not connected'):
        await storage.close()
    assert await storage.connect() is None
    with pytest.raises(RuntimeError, match='Already connected'):
        await storage.connect()
    assert await storage.set('key1', {'key2': 'value2'}) is None
    assert await storage.get('key1') == {'key2': 'value2'}
    assert await storage.get('key2') is None
    assert await storage.set('key2', {'key3': 'value3'}) is None

    items1 = []
    async for item in storage.iterate('k'):
        items1.append(item)
    assert items1 == [
        ('key1', {'key2': 'value2'}),
        ('key2', {'key3': 'value3'})
    ]

    items2 = []
    async for item in storage.iterate('key1'):
        items2.append(item)
    assert items2 == [('key1', {'key2': 'value2'})]

    items3 = []
    async for item in storage.iterate():
        items3.append(item)
    assert items3 == [
        ('key1', {'key2': 'value2'}),
        ('key2', {'key3': 'value3'})
    ]

    assert await storage.delete('key1') is None
    assert await storage.get('key2') == {'key3': 'value3'}
    assert await storage.clear() is None

    items4 = []
    async for item in storage.iterate():
        items4.append(item)
    assert items4 == []

    assert isinstance(storage.raw_connection(), aiosqlite.Connection)

    assert await storage.close() is None
