import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from aiotgbot.storage import StorageProtocol
from aiotgbot.storage_sqlalchemy import SqlalchemyStorage

pytestmark = pytest.mark.asyncio


async def test_sqlalchemy_postgres_storage(postgres_engine: AsyncEngine) -> None:
    """Integration test: Postgres via SQLAlchemy + testcontainers."""

    storage: StorageProtocol = SqlalchemyStorage(postgres_engine)

    await storage.connect()
    await storage.clear()

    await storage.set("key1", {"key2": "value2"})
    assert await storage.get("key1") == {"key2": "value2"}
    assert await storage.get("missing") is None

    await storage.set("key2", {"key3": "value3"})

    iter_keys = [k async for k, _ in storage.iterate("k")]
    assert set(iter_keys) == {"key1", "key2"}

    iter_key1 = [item async for item in storage.iterate("key1")]
    assert iter_key1 == [("key1", {"key2": "value2"})]

    iter_all = [item async for item in storage.iterate()]
    assert sorted(iter_all, key=lambda item: item[0]) == [
        ("key1", {"key2": "value2"}),
        ("key2", {"key3": "value3"}),
    ]

    await storage.delete("key1")
    assert await storage.get("key2") == {"key3": "value3"}

    await storage.clear()
    assert [item async for item in storage.iterate()] == []

    assert isinstance(storage.raw_connection(), AsyncEngine)
