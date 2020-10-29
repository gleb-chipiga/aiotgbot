import asyncio
import json
from contextlib import asynccontextmanager, suppress
from functools import partial
from html import escape
from typing import AsyncGenerator, Dict, Final, Hashable, Optional, Tuple

from aiotgbot.api_types import MessageEntity
from aiotgbot.constants import MessageEntityType

json_dumps = partial(json.dumps, ensure_ascii=False)


class KeyLock:
    __slots__ = ('_keys',)

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


class FreqLimit:
    __slots__ = ('_interval', '_clean_interval', '_events', '_ts',
                 '_clean_event', '_clean_task')

    def __init__(self, interval: float, clean_interval: float = 0) -> None:
        self._interval: Final[float] = interval
        self._clean_interval: Final[float] = (
            clean_interval if clean_interval > 0 else interval)
        self._events: Final[Dict[Hashable, asyncio.Event]] = {}
        self._ts: Final[Dict[Hashable, float]] = {}
        self._clean_event: Final = asyncio.Event()
        self._clean_task: Optional[asyncio.Task] = None

    async def reset(self) -> None:
        if self._clean_task is not None:
            self._clean_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._clean_task
            self._clean_task = None
        self._events.clear()
        self._ts.clear()
        self._clean_event.clear()

    @asynccontextmanager
    async def acquire(self, key: Hashable) -> AsyncGenerator[None, None]:
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
            if len(self._events) == 0:
                await self._clean_event.wait()
                self._clean_event.clear()
            for key, event in self._events.copy().items():
                age = loop.time() - self._ts[key]
                if event.is_set() and age >= self._clean_interval:
                    del self._events[key]
            for key in self._ts.copy().keys():
                if key not in self._events:
                    del self._ts[key]
            await asyncio.sleep(self._clean_interval)


def _entity_tag(text: str, entity: MessageEntity) -> Optional[str]:
    if entity.type == MessageEntityType.BOLD:
        tag = f'<b>{text}</b>'
    elif entity.type == MessageEntityType.ITALIC:
        tag = f'<i>{text}</i>'
    elif entity.type == MessageEntityType.UNDERLINE:
        tag = f'<u>{text}</u>'
    elif entity.type == MessageEntityType.STRIKETHROUGH:
        tag = f'<s>{text}</s>'
    elif entity.type == MessageEntityType.CODE:
        tag = f'<code>{text}</code>'
    elif entity.type == MessageEntityType.PRE and entity.language is not None:
        code_tag = f'<code class="language-{entity.language}">{text}</code>'
        tag = f'<pre>{code_tag}</pre>'
    elif entity.type == MessageEntityType.PRE:
        tag = f'<pre><code>{text}</code></pre>'
    elif entity.type == MessageEntityType.EMAIL:
        tag = f'<a href="mailto:{text}">{text}</a>'
    elif entity.type == MessageEntityType.URL:
        tag = f'<a href="{text}">{text}</a>'
    elif entity.type == MessageEntityType.TEXT_LINK:
        assert entity.url is not None
        tag = f'<a href="{escape(entity.url)}">{text}</a>'
    elif entity.type == MessageEntityType.TEXT_MENTION:
        assert entity.user is not None
        tag = f'<a href="tg://user?id={entity.user.id}">{text}</a>'
    else:
        return None

    return tag


_MessageEntities = Tuple[MessageEntity, ...]


def _message_to_html(text: str, entities: Optional[_MessageEntities],
                     offset: int = 0, length: Optional[int] = None) -> str:
    if len(text) == 0:
        return text
    elif entities is None or len(entities) == 0:
        return escape(text)

    utf16 = text.encode('utf-16-le')
    if length is None:
        length = len(utf16)
    result = ''
    last_offset = 0
    for index, entity in enumerate(entities):
        if entity.offset >= offset + length:
            break
        relative_offset = entity.offset - offset
        if relative_offset > last_offset:
            part = utf16[last_offset * 2:relative_offset * 2]
            result += escape(part.decode('utf-16-le'))
        elif relative_offset < last_offset:
            continue
        part = utf16[relative_offset * 2:(relative_offset + entity.length) * 2]
        entity_text = _message_to_html(
            part.decode('utf-16-le'), entities[index + 1:],
            entity.offset, entity.length
        )
        tag = _entity_tag(entity_text, entity)
        if tag is not None:
            last_offset = relative_offset + entity.length
            result += tag
        else:
            last_offset = relative_offset
    part = utf16[last_offset * 2:]
    result += escape(part.decode('utf-16-le'))

    return result


def message_to_html(text: str, entities: Optional[_MessageEntities]) -> str:
    return _message_to_html(text, entities)
