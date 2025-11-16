from collections.abc import AsyncIterator
from typing import Final, cast

from sqlalchemy import JSON, Text, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing_extensions import override  # Python 3.11 compatibility

from .helpers import Json
from .storage import StorageProtocol

__all__ = ("SqlalchemyStorage",)


class Base(DeclarativeBase):
    pass


class KV(Base):
    __tablename__: str = "kv"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[Json] = mapped_column(JSON)


class SqlalchemyStorage(StorageProtocol):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine: Final = engine

    @override
    async def connect(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    @override
    async def close(self) -> None:
        pass

    @override
    async def set(self, key: str, value: Json | None = None) -> None:
        async with self._engine.begin() as connection:
            try:
                async with connection.begin_nested():
                    _ = await connection.execute(
                        insert(KV).values(key=key, value=value)
                    )
            except IntegrityError:
                _ = await connection.execute(
                    update(KV).where(KV.key == key).values(value=value)
                )

    @override
    async def get(self, key: str) -> Json:
        async with self._engine.begin() as connection:
            result = await connection.execute(select(KV.value).where(KV.key == key))
            return result.scalar()

    @override
    async def delete(self, key: str) -> None:
        async with self._engine.begin() as connection:
            _ = await connection.execute(delete(KV).where(KV.key == key))

    @override
    async def iterate(
        self,
        prefix: str = "",
    ) -> AsyncIterator[tuple[str, Json]]:
        async with self._engine.begin() as connection:
            stream = cast(
                AsyncIterator[tuple[str, Json]],
                await connection.stream(
                    select(KV.key, KV.value).where(KV.key.startswith(prefix))
                ),
            )
            async for key, value in stream:
                yield key, value

    @override
    async def clear(self) -> None:
        async with self._engine.begin() as connection:
            _ = await connection.execute(delete(KV))

    @override
    def raw_connection(self) -> AsyncEngine:
        return self._engine
