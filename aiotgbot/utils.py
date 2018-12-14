import asyncio
from contextlib import asynccontextmanager, suppress
from functools import partial
from html import escape
from typing import Any, AsyncGenerator, Dict, Iterable, Optional

from .api_types import MessageEntity
from .constants import MessageEntityType

try:
    import ujson as json
except ImportError:  # pragma: no cover
    import json  # type: ignore

json_dumps = partial(json.dumps, ensure_ascii=False,
                     escape_forward_slashes=False)


def entity_to_html(entity: MessageEntity, message_text: str) -> str:
    if message_text == '':
        return message_text

    message_bytes = message_text.encode('utf-16-le')
    entity_bytes = message_bytes[entity.offset * 2:(entity.offset +
                                                    entity.length) * 2]
    entity_text = entity_bytes.decode('utf-16-le')

    if entity.type == MessageEntityType.BOLD:
        return f'<b>{escape(entity_text)}</b>'
    elif entity.type == MessageEntityType.ITALIC:
        return f'<i>{escape(entity_text)}</i>'
    elif entity.type == MessageEntityType.PRE:
        return f'<pre>{escape(entity_text)}</pre>'
    elif entity.type == MessageEntityType.CODE:
        return f'<code>{escape(entity_text)}</code>'
    elif entity.type == MessageEntityType.TEXT_LINK:
        return f'<a href="{entity.url}">{escape(entity_text)}</a>'
    elif (entity.type == MessageEntityType.TEXT_MENTION and
          entity.user is not None):
        username = entity.user.username
        return f'<a href="https://t.me/{username}">{escape(entity_text)}</a>'
    else:
        return entity_text


def entities_to_html(entities: Optional[Iterable[MessageEntity]],
                     message_text: str) -> str:
    if entities is None:
        return message_text

    message_bytes = message_text.encode('utf-16-le')
    result = ''
    offset = 0

    for entity in sorted(entities, key=lambda _entity: _entity.offset):
        entity_text = entity_to_html(entity, message_text)

        part = message_bytes[offset * 2:entity.offset * 2]
        result += escape(part.decode('utf-16-le')) + entity_text

        offset = entity.offset + entity.length

    part = message_bytes[offset * 2:]
    result += escape(part.decode('utf-16-le'))

    return result


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
        self._interval = interval
        self._clean_interval = (clean_interval if clean_interval > 0
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
