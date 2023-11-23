import json
from typing import Annotated, Any, AsyncIterator, Final, Tuple, cast

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from aiotgbot.helpers import json_dumps
from aiotgbot.storage import Json, StorageProtocol

__all__ = ("SqlalchemyStorage",)


class Base(DeclarativeBase):
    pass


class KV(Base):
    __tablename__ = "kv"

    key: Mapped[Annotated[str, mapped_column(primary_key=True)]]
    value: Mapped[str]


class SqlalchemyStorage(StorageProtocol):
    def __init__(self, url: str) -> None:
        self._engine: Final = create_async_engine(url)

    async def connect(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()

    async def set(self, key: str, value: Json = None) -> None:
        json_value = json_dumps(value)
        async with self._engine.begin() as connection:
            try:
                await connection.execute(
                    insert(KV).values(key=key, value=json_value)
                )
            except IntegrityError:
                await connection.execute(
                    update(KV).where(KV.key == key).values(value=json_value)
                )

    async def get(self, key: str) -> Json:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                select(KV.value).where(KV.key == key)
            )
            value = result.scalar()
            if value is not None:
                return cast(Json, json.loads(value))
            else:
                return None

    async def delete(self, key: str) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(delete(KV).where(KV.key == key))

    async def iterate(
        self, prefix: str = ""
    ) -> AsyncIterator[Tuple[str, Json]]:
        async with self._engine.begin() as connection:
            result = await connection.stream(
                select(KV.key, KV.value).where(KV.key.startswith(prefix))
            )
            async for key, value in result:
                yield key, json.loads(value)

    async def clear(self) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(delete(KV))

    def raw_connection(self) -> Any:
        return self._engine
