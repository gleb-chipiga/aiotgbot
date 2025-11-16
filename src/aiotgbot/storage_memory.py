from collections.abc import AsyncIterator
from typing import Final

from typing_extensions import override  # Python 3.11 compatibility

from .helpers import Json
from .storage import StorageProtocol

__all__ = ("MemoryStorage",)


class MemoryStorage(StorageProtocol):
    def __init__(self) -> None:
        self._data: Final[dict[str, Json]] = {}

    @override
    async def connect(self) -> None: ...

    @override
    async def close(self) -> None: ...

    @override
    async def set(self, key: str, value: Json = None) -> None:
        self._data[key] = value

    @override
    async def get(self, key: str) -> Json:
        return self._data.get(key)

    @override
    async def delete(self, key: str) -> None:
        _ = self._data.pop(key, None)

    @override
    async def iterate(self, prefix: str = "") -> AsyncIterator[tuple[str, Json]]:
        for key, value in self._data.items():
            if key.startswith(prefix):
                yield key, value

    @override
    async def clear(self) -> None:
        self._data.clear()

    @override
    def raw_connection(self) -> object:
        return None
