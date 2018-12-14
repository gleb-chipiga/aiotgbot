import asyncio
import random

import pytest

from aiotgbot.api_types import MessageEntity, User
from aiotgbot.utils import FreqLimit, KeyLock, entities_to_html, entity_to_html

TEXT = 'обычный наклонный жирный код1 код2 ссылка @BotSupport чел текст'
ENTITIES = (
    MessageEntity(type='italic', offset=8, length=9, url=None, user=None),
    MessageEntity(type='bold', offset=18, length=6, url=None, user=None),
    MessageEntity(type='code', offset=25, length=4, url=None, user=None),
    MessageEntity(type='pre', offset=30, length=4, url=None, user=None),
    MessageEntity(type='text_link', offset=35, length=6,
                  url='https://core.telegram.org/bots/api', user=None),
    MessageEntity(type='mention', offset=42, length=11, url=None, user=None),
    MessageEntity(type='text_mention', offset=54, length=3,
                  url=None, user=User(id=1, is_bot=False, first_name='Fname',
                                      last_name='Lname', username='username',
                                      language_code=None,
                                      sticker_set_name=None,
                                      can_set_sticker_set=None))
)


def test_entity_to_html_empty():
    assert entity_to_html(ENTITIES[0], '') == ''


@pytest.mark.parametrize('index, expected', (
    (0, '<i>наклонный</i>'),
    (1, '<b>жирный</b>'),
    (2, '<code>код1</code>'),
    (3, '<pre>код2</pre>'),
    (4, '<a href="https://core.telegram.org/bots/api">ссылка</a>'),
    (5, '@BotSupport'),
    (6, '<a href="https://t.me/username">чел</a>')
))
def test_entity_to_html(index, expected):
    assert entity_to_html(ENTITIES[index], TEXT) == expected


def test_entities_to_html_none_entities():
    assert entities_to_html(None, TEXT) == TEXT


def test_entities_to_html_empty_entities():
    assert entities_to_html([], TEXT) == TEXT


def test_entities_to_html():
    assert entities_to_html(ENTITIES, TEXT) == (
        'обычный <i>наклонный</i> <b>жирный</b> <code>код1</code> '
        '<pre>код2</pre> '
        '<a href="https://core.telegram.org/bots/api">ссылка</a> '
        '@BotSupport <a href="https://t.me/username">чел</a> текст')


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

    tasks = (limit(freq_limit, random.uniform(0, .1)) for _ in range(5))
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
