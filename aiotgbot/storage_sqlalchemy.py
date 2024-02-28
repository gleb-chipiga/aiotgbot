from typing import Annotated, Any, AsyncIterator, Final

from sqlalchemy import JSON, Text, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .helpers import Json
from .storage import StorageProtocol

__all__ = ("SqlalchemyStorage",)


class Base(DeclarativeBase):
    pass


class KV(Base):
    __tablename__ = "kv"

    key: Mapped[Annotated[str, mapped_column(Text, primary_key=True)]]
    value: Mapped[Annotated[Json, mapped_column(JSON)]]


class SqlalchemyStorage(StorageProtocol):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine: Final = engine

    async def connect(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        pass

    async def set(self, key: str, value: Json = None) -> None:
        async with self._engine.begin() as connection:
            try:
                async with connection.begin_nested():
                    await connection.execute(
                        insert(KV).values(key=key, value=value)
                    )
            except IntegrityError:
                await connection.execute(
                    update(KV).where(KV.key == key).values(value=value)
                )

    async def get(self, key: str) -> Json:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                select(KV.value).where(KV.key == key)
            )
            return result.scalar()

    async def delete(self, key: str) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(delete(KV).where(KV.key == key))

    async def iterate(
        self,
        prefix: str = "",
    ) -> AsyncIterator[tuple[str, Json]]:
        async with self._engine.begin() as connection:
            result = await connection.stream(
                select(KV.key, KV.value).where(KV.key.startswith(prefix))
            )
            async for key, value in result:
                yield key, value

    async def clear(self) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(delete(KV))

    def raw_connection(self) -> Any:
        return self._engine
