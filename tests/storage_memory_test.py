import pytest

from aiotgbot import StorageProtocol
from aiotgbot.storage_memory import MemoryStorage


def test_storage_protocol() -> None:
    storage: StorageProtocol = MemoryStorage()
    assert isinstance(storage, StorageProtocol)


@pytest.mark.asyncio
async def test_sqlite_storage() -> None:
    storage: StorageProtocol = MemoryStorage()
    await storage.connect()
    await storage.set("key1", {"key2": "value2"})
    assert await storage.get("key1") == {"key2": "value2"}
    await storage.get("key2")
    await storage.set("key2", {"key3": "value3"})

    items1 = []
    async for item in storage.iterate("k"):
        items1.append(item)
    assert items1 == [
        ("key1", {"key2": "value2"}),
        ("key2", {"key3": "value3"}),
    ]

    items2 = []
    async for item in storage.iterate("key1"):
        items2.append(item)
    assert items2 == [("key1", {"key2": "value2"})]

    items3 = []
    async for item in storage.iterate():
        items3.append(item)
    assert items3 == [
        ("key1", {"key2": "value2"}),
        ("key2", {"key3": "value3"}),
    ]

    await storage.delete("key1")
    assert await storage.get("key2") == {"key3": "value3"}
    await storage.clear()

    items4 = []
    async for item in storage.iterate():
        items4.append(item)
    assert items4 == []

    assert storage.raw_connection() is None

    await storage.close()
