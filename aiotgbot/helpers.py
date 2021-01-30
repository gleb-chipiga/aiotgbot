import asyncio
import json
from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncGenerator, Dict, Final, Hashable

json_dumps: Final = partial(json.dumps, ensure_ascii=False)


def get_python_version() -> str:
    from sys import version_info as version
    return f'{version.major}.{version.minor}.{version.micro}'


def get_software() -> str:
    from . import __version__
    return f'Python/{get_python_version()} aiotgbot/{__version__}'


class KeyLock:
    __slots__ = '_keys'

    def __init__(self) -> None:
        self._keys: Final[Dict[Hashable, asyncio.Event]] = {}

    @asynccontextmanager
    async def acquire(self, key: Hashable) -> AsyncGenerator[None, None]:
        while key in self._keys:
            await self._keys[key].wait()
        self._keys[key] = asyncio.Event()
        try:
            yield
        finally:
            self._keys.pop(key).set()
