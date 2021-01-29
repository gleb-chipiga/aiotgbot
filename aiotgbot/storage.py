from abc import abstractmethod
from typing import AsyncIterator, Protocol, Tuple, runtime_checkable

from aiotgbot.helpers import Json


@runtime_checkable
class StorageProtocol(Protocol):

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def set(self, key: str, value: Json = None) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> Json: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    def iterate(self, prefix: str = '') -> AsyncIterator[Tuple[str, Json]]: ...

    @abstractmethod
    async def clear(self) -> None: ...
