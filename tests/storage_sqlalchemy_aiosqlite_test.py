from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from aiotgbot.storage import StorageProtocol
from aiotgbot.storage_sqlalchemy import SqlalchemyStorage

pytestmark = pytest.mark.asyncio


async def test_sqlalchemy_aiosqlite(tmp_path: Path) -> None:
    """Integration test for SQLAlchemy storage on aiosqlite driver."""

    db_path = tmp_path / "test.sqlite3"
    engine: AsyncEngine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    storage: StorageProtocol = SqlalchemyStorage(engine)

    await storage.connect()
    await storage.set("key", {"v": 1})
    assert await storage.get("key") == {"v": 1}

    items = [item async for item in storage.iterate()]
    assert items == [("key", {"v": 1})]

    await storage.clear()
    assert [item async for item in storage.iterate()] == []

    assert isinstance(storage.raw_connection(), AsyncEngine)

    await engine.dispose()
