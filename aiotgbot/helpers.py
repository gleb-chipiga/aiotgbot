import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Final, Hashable
from weakref import WeakValueDictionary

import msgspec.json
from aiohttp import web

__all__ = (
    "BotKey",
    "Json",
    "KeyLock",
    "get_python_version",
    "get_software",
    "json_dumps",
)

Json = str | int | float | bool | dict[str, "Json"] | list["Json"] | None


def json_dumps(obj: Json) -> str:
    return msgspec.json.encode(obj).decode()


def get_python_version() -> str:
    from sys import version_info as version

    return f"{version.major}.{version.minor}.{version.micro}"


def get_software() -> str:
    from . import __version__

    return f"Python/{get_python_version()} aiotgbot/{__version__}"


class KeyLock:
    def __init__(self) -> None:
        self._locks: "Final[WeakValueDictionary[Hashable," "asyncio.Lock]]" = (
            WeakValueDictionary()
        )

    @asynccontextmanager
    async def resource(self, key: Hashable) -> AsyncIterator[None]:
        if key not in self._locks:
            lock = asyncio.Lock()
            self._locks[key] = lock
        else:
            lock = self._locks[key]
        async with lock:
            yield


BotKey = web.AppKey
