import asyncio
from html import escape
from random import uniform

import pytest
from hypothesis import given
from hypothesis.strategies import builds, integers, text

from aiotgbot.api_types import MessageEntity, User
from aiotgbot.constants import MessageEntityType
from aiotgbot.utils import FreqLimit, KeyLock, _entity_tag, message_to_html


@pytest.mark.asyncio
async def test_sleep():
    loop = asyncio.get_running_loop()
    time1 = loop.time()
    assert await asyncio.sleep(.1) is None
    time2 = loop.time()

    assert .09 < time2 - time1 < .11


@pytest.mark.asyncio
async def test_key_lock():
    key_lock = KeyLock()
    loop = asyncio.get_running_loop()

    async def lock(_key_lock):
        time1 = loop.time()
        async with _key_lock.acquire('test'):
            time2 = loop.time()
            await asyncio.sleep(.1)
            time3 = loop.time()
        return time2, time3, time2 - time1

    intervals = await asyncio.gather(lock(key_lock), lock(key_lock),
                                     lock(key_lock))
    intervals = sorted(intervals, key=lambda i: i[0])
    assert intervals[0][2] < .01
    assert .09 < intervals[1][2] < .11
    assert .11 < intervals[2][2] < .21
    assert intervals[0][1] < intervals[1][0]
    assert intervals[1][1] < intervals[2][0]


@pytest.mark.asyncio
async def test_freq_limit():
    freq_limit = FreqLimit(.1, .1)
    loop = asyncio.get_running_loop()

    async def limit(_freq_limit, interval):
        time1 = loop.time()
        async with _freq_limit.acquire('test'):
            time2 = loop.time()
            await asyncio.sleep(interval)
            time3 = loop.time()
            assert _freq_limit._events.keys() == _freq_limit._ts.keys()
        return time2, time3, time2 - time1

    tasks = (limit(freq_limit, uniform(0, .1)) for _ in range(5))
    intervals = await asyncio.gather(*tasks)
    intervals = sorted(intervals, key=lambda interval: interval[0])
    for i in range(len(intervals)):
        if i + 1 < len(intervals):
            assert intervals[i + 1][0] - intervals[i][0] > .1
            assert intervals[i][1] < intervals[i + 1][0]

    assert freq_limit._events.keys() == freq_limit._ts.keys()
    await asyncio.sleep(.2)
    assert not freq_limit._events
    await freq_limit.reset()


@given(offset=integers(0, 4096), length=integers(0, 4096))
@pytest.mark.parametrize('type_, language, url, user, expected', (
    (MessageEntityType.BOLD, None, None, None, '<b>текст</b>'),
    (MessageEntityType.ITALIC, None, None, None, '<i>текст</i>'),
    (MessageEntityType.UNDERLINE, None, None, None, '<u>текст</u>'),
    (MessageEntityType.STRIKETHROUGH, None, None, None, '<s>текст</s>'),
    (MessageEntityType.CODE, None, None, None, '<code>текст</code>'),
    (MessageEntityType.PRE, None, None, None, '<pre><code>текст</code></pre>'),
    (MessageEntityType.PRE, 'python', None, None,
     '<pre><code class="language-python">текст</code></pre>'),
    (MessageEntityType.EMAIL, None, None, None,
     '<a href="mailto:текст">текст</a>'),
    (MessageEntityType.URL, None, None, None, '<a href="текст">текст</a>'),
    (MessageEntityType.TEXT_LINK, None, 'https://t.me', None,
     '<a href="https://t.me">текст</a>'),
    (MessageEntityType.TEXT_MENTION, None, None, User(1, False, 'name'),
     '<a href="tg://user?id=1">текст</a>')
))
def test_entity_tag(type_, offset, length, language, url, user, expected):
    entity = MessageEntity(type_, offset, length, url, user, language)
    assert _entity_tag('текст', entity) == expected


@given(txt=text(), offset=integers(0, 4096), length=integers(0, 4096))
@pytest.mark.parametrize('type_', (
    MessageEntityType.MENTION,
    MessageEntityType.HASHTAG,
    MessageEntityType.CASHTAG,
    MessageEntityType.BOT_COMMAND,
    MessageEntityType.PHONE_NUMBER
))
def test_entity_tag_unknown_entity_types(txt, type_, offset, length):
    entity = MessageEntity(type_, offset, length)
    assert _entity_tag(txt, entity) is None


@given(builds(MessageEntity))
def test_message_to_html_empty_text(entity):
    assert message_to_html('', entity) == ''


@given(txt=text())
@pytest.mark.parametrize('entities', ((), None))
def test_message_to_html_empty_entities(txt, entities):
    assert message_to_html(txt, entities) == escape(txt)


def test_message_to_html():
    txt = ('перечеркнутый обычный наклонный жирный код1 код2 🎲ссылка 📈😊 '
           '@test чел текст подчеркнутый')
    entities = (
        MessageEntity(MessageEntityType.STRIKETHROUGH, 0, 13),
        MessageEntity(MessageEntityType.ITALIC, 22, 16),
        MessageEntity(MessageEntityType.BOLD, 32, 6),
        MessageEntity(MessageEntityType.CODE, 39, 4),
        MessageEntity(MessageEntityType.PRE, 44, 4),
        MessageEntity(MessageEntityType.TEXT_LINK, 51, 9, url='https://t.me'),
        MessageEntity(MessageEntityType.MENTION, 63, 5),
        MessageEntity(MessageEntityType.TEXT_MENTION, 69, 3,
                      user=User(1, False, 'name')),
        MessageEntity(MessageEntityType.UNDERLINE, 79, 12),
    )

    assert message_to_html(txt, entities) == (
        '<s>перечеркнутый</s> обычный <i>наклонный <b>жирный</b></i> '
        '<code>код1</code> <pre><code>код2</code></pre> '
        '🎲<a href="https://t.me">ссылка 📈</a>😊 '
        '@test <a href="tg://user?id=1">чел</a> текст <u>подчеркнутый</u>')
