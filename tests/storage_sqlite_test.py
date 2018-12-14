import pytest

from aiotgbot.storage_sqlite import SQLiteStorage


@pytest.mark.asyncio
async def test_sqlite_storage(tmpdir):
    storage = SQLiteStorage(tmpdir / 'test.sqlite')
    assert await storage.set('key1', {'key2': 'value2'}) is None
    assert await storage.get('key1') == {'key2': 'value2'}
    assert await storage.get('key2') is None
    assert await storage.set('key2', {'key3': 'value3'}) is None
    assert await storage.keys('k') == ('key1', 'key2')
    assert await storage.delete('key1') is None
    assert await storage.get('key2') == {'key3': 'value3'}
    assert await storage.reset_all() is None
    assert await storage.keys('') == tuple()
    assert await storage.close() is None
