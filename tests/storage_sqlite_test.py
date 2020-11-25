import pytest

from aiotgbot.storage_sqlite import SQLiteStorage


@pytest.mark.asyncio
async def test_sqlite_storage(tmpdir):
    storage = SQLiteStorage(tmpdir / 'test.sqlite')
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

    assert await storage.delete('key1') is None
    assert await storage.get('key2') == {'key3': 'value3'}
    assert await storage.clear() is None

    items2 = []
    async for item in storage.iterate():
        items2.append(item)
    assert items2 == []

    assert await storage.close() is None
