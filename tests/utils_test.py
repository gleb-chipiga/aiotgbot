import asyncio
import random

import pytest

from aiotgbot.utils import FreqLimit, KeyLock


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
