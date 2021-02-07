import asyncio
import json
from asyncio import Task
from contextlib import asynccontextmanager
from functools import partial
from inspect import isasyncgenfunction
from signal import SIGINT, SIGTERM
from typing import (Any, AsyncGenerator, AsyncIterator, Callable, Dict, Final,
                    Hashable, Iterator, MutableMapping, Optional)

__all__ = ('json_dumps', 'get_python_version', 'get_software', 'KeyLock',
           'ContextFunction', 'Runner')


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


ContextFunction = Callable[['Runner'], AsyncIterator[None]]


class Runner(MutableMapping[str, Any]):

    def __init__(
        self, context_function: ContextFunction, debug: bool = False
    ) -> None:
        if not isasyncgenfunction(context_function):
            raise RuntimeError('Argument is not async generator')
        self._context_function: Final[ContextFunction] = context_function
        self._debug: Final[bool] = debug
        self._wait_task: Optional[Task[None]] = None
        self._started: bool = False
        self._stopped: bool = False
        self._data: Final[Dict[str, Any]] = {}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    async def _run(self) -> None:
        assert not self._started
        assert not self._stopped
        self._started = True
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(SIGINT, self.stop)
        loop.add_signal_handler(SIGTERM, self.stop)
        iterator = self._context_function(self).__aiter__()
        await iterator.__anext__()
        self._wait_task = asyncio.create_task(self._wait())
        try:
            await self._wait_task
        except asyncio.CancelledError:
            pass
        try:
            await iterator.__anext__()
        except StopAsyncIteration:
            pass
        else:
            raise RuntimeError(f'{iterator!r} has more than one \'yield\'')

    async def _wait(self) -> None:
        assert self._started
        assert not self._stopped
        while not self._stopped:
            await asyncio.sleep(3600)

    def stop(self) -> None:
        if not self._started:
            raise RuntimeError('Not started')
        if self._stopped:
            raise RuntimeError('Already stopped')
        assert self._wait_task is not None
        self._stopped = True
        self._wait_task.cancel()

    def run(self) -> None:
        if self._started:
            raise RuntimeError('Already started')
        asyncio.run(self._run(), debug=self._debug)
