from typing import Any, Dict, Tuple

from .storage import BaseStorage


class MemoryStorage(BaseStorage):

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    async def close(self): ...

    async def set(self, key: str, value: Any = None) -> None:
        self._data[key] = value

    async def get(self, key: str) -> Any:
        return self._data.get(key)

    async def delete(self, key: str) -> None:
        del self._data[key]

    async def keys(self, prefix: str) -> Tuple[str, ...]:
        return tuple(k for k in self._data if k.startswith(prefix))

    async def reset_all(self) -> None:
        self._data = {}
