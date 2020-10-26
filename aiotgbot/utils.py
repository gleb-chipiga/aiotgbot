import asyncio
import json
from contextlib import asynccontextmanager, suppress
from functools import partial
from typing import Any, AsyncGenerator, Dict, Final, Optional

json_dumps = partial(json.dumps, ensure_ascii=False)


class KeyLock:
    __slots__ = ('_keys',)

    def __init__(self) -> None:
        self._keys: Dict[Any, asyncio.Event] = {}

    @asynccontextmanager
    async def acquire(self, key: Any) -> AsyncGenerator[None, None]:
        while key in self._keys:
            await self._keys[key].wait()
        self._keys[key] = asyncio.Event()
        try:
            yield
        finally:
            self._keys.pop(key).set()


class FreqLimit:
    __slots__ = ('_interval', '_clean_interval', '_events', '_ts',
                 '_clean_event', '_clean_task')

    def __init__(self, interval: float, clean_interval: float = 0) -> None:
        self._interval: Final = interval
        self._clean_interval: Final = (clean_interval if clean_interval > 0
                                       else interval)
        self._events: Dict[Any, asyncio.Event] = {}
        self._ts: Dict[Any, float] = {}
        self._clean_event = asyncio.Event()
        self._clean_task: Optional[asyncio.Task] = None

    async def reset(self) -> None:
        if self._clean_task is not None:
            self._clean_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._clean_task
            self._clean_task = None
        self._events = {}
        self._ts = {}
        self._clean_event.clear()

    @asynccontextmanager
    async def acquire(self, key) -> AsyncGenerator[None, None]:
        loop = asyncio.get_running_loop()
        if self._clean_task is None:
            self._clean_task = loop.create_task(self._clean())
        while True:
            if key not in self._events:
                self._events[key] = asyncio.Event()
                self._ts[key] = -float('inf')
                break
            else:
                await self._events[key].wait()
                if key in self._events and self._events[key].is_set():
                    self._events[key].clear()
                    break
        delay = self._interval - loop.time() + self._ts[key]
        if delay > 0:
            await asyncio.sleep(delay)
        self._ts[key] = loop.time()
        try:
            yield
        finally:
            self._events[key].set()
            self._clean_event.set()

    async def _clean(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            if not self._events:
                await self._clean_event.wait()
                self._clean_event.clear()
            self._events = {key: event for key, event in self._events.items()
                            if not event.is_set() or loop.time() -
                            self._ts[key] < self._clean_interval}
            self._ts = {key: ts for key, ts in self._ts.items()
                        if key in self._events}
            await asyncio.sleep(self._clean_interval)
