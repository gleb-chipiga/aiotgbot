from abc import ABC, abstractmethod
from typing import Any, Tuple


class BaseStorage(ABC):

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def set(self, key: str, value: Any = None) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> Any: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def keys(self, prefix: str) -> Tuple[str, ...]: ...

    @abstractmethod
    async def reset_all(self) -> None: ...
