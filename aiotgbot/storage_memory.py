from typing import Any, AsyncIterator, Final

from .helpers import Json
from .storage import StorageProtocol

__all__ = ("MemoryStorage",)


class MemoryStorage(StorageProtocol):
    def __init__(self) -> None:
        self._data: Final[dict[str, Any]] = {}

    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def set(self, key: str, value: Json = None) -> None:
        self._data[key] = value

    async def get(self, key: str) -> Json:
        return self._data.get(key)

    async def delete(self, key: str) -> None:
        self._data.pop(key)

    async def iterate(
        self, prefix: str = ""
    ) -> AsyncIterator[tuple[str, Json]]:
        for key, value in self._data.items():
            if key.startswith(prefix):
                yield key, value

    async def clear(self) -> None:
        self._data.clear()

    def raw_connection(self) -> Any:
        return None
