import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from aiotgbot import StorageProtocol
from aiotgbot.helpers import Json
from aiotgbot.storage_sqlalchemy import SqlalchemyStorage

KeyValue = tuple[str, Json]


def test_storage_protocol() -> None:
    engine = create_async_engine("sqlite+aiosqlite://")
    storage: StorageProtocol = SqlalchemyStorage(engine)
    assert isinstance(storage, StorageProtocol)


@pytest.mark.asyncio
async def test_sqlalchemy_storage() -> None:
    engine = create_async_engine("sqlite+aiosqlite://")
    storage: StorageProtocol = SqlalchemyStorage(engine)
    await storage.connect()
    await storage.set("key11", "value22")
    assert await storage.get("key11") == "value22"
    await storage.delete("key11")

    await storage.set("key1", {"key2": "value2"})
    await storage.set("key1", {"key2": "value2"})
    assert await storage.get("key1") == {"key2": "value2"}
    assert await storage.get("key2") is None
    await storage.set("key2", {"key3": "value3"})

    items1: list[KeyValue] = []
    async for item in storage.iterate("k"):
        items1.append(item)
    assert items1 == [
        ("key1", {"key2": "value2"}),
        ("key2", {"key3": "value3"}),
    ]

    items2: list[KeyValue] = []
    async for item in storage.iterate("key1"):
        items2.append(item)
    assert items2 == [("key1", {"key2": "value2"})]

    items3: list[KeyValue] = []
    async for item in storage.iterate():
        items3.append(item)
    assert items3 == [
        ("key1", {"key2": "value2"}),
        ("key2", {"key3": "value3"}),
    ]

    await storage.delete("key1")
    assert await storage.get("key2") == {"key3": "value3"}
    await storage.clear()

    items4: list[KeyValue] = []
    async for item in storage.iterate():
        items4.append(item)
    assert items4 == []

    assert isinstance(storage.raw_connection(), AsyncEngine)

    await storage.close()
