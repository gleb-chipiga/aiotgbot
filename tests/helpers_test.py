import asyncio
from typing import List, Tuple, cast
from weakref import ref

import pytest

from aiotgbot.helpers import KeyLock


@pytest.mark.asyncio
async def test_sleep() -> None:
    loop = asyncio.get_running_loop()
    time1 = loop.time()
    assert await asyncio.sleep(.1) is None
    time2 = loop.time()

    assert .09 < time2 - time1 < .11


@pytest.mark.asyncio
async def test_key_lock_intervals() -> None:
    key_lock = KeyLock()
    loop = asyncio.get_running_loop()

    time_marks = Tuple[float, float, float]

    async def lock(_key_lock: KeyLock) -> time_marks:
        time1 = loop.time()
        async with _key_lock.resource('key'):
            time2 = loop.time()
            await asyncio.sleep(.1)
            time3 = loop.time()
        return time2, time3, time2 - time1

    tasks = (lock(key_lock), lock(key_lock), lock(key_lock))
    intervals = cast(List[time_marks], await asyncio.gather(*tasks))
    intervals = sorted(intervals, key=lambda i: i[0])
    assert intervals[0][2] < .01
    assert .09 < intervals[1][2] < .11
    assert .11 < intervals[2][2] < .21
    assert intervals[0][1] < intervals[1][0]
    assert intervals[1][1] < intervals[2][0]

    assert tuple(key_lock._locks) == ()


@pytest.mark.asyncio
async def test_key_lock_keys() -> None:
    key_lock = KeyLock()
    assert tuple(key_lock._locks) == ()
    async with key_lock.resource('key2'):
        assert tuple(key_lock._locks.keys()) == ('key2',)
        async with key_lock.resource('key3'):
            assert tuple(key_lock._locks.keys()) == ('key2', 'key3')
            async with key_lock.resource('key4'):
                assert tuple(key_lock._locks.keys()) == (
                    'key2', 'key3', 'key4')
        assert tuple(key_lock._locks.keys()) == ('key2',)
    assert tuple(key_lock._locks) == ()


@pytest.mark.asyncio
async def test_key_lock_overlaps() -> None:

    async def task1(_key_lock: KeyLock) -> None:
        async with _key_lock.resource('key1'):
            assert tuple(_key_lock._locks) == ('key1',)
            await asyncio.sleep(.1)
            assert tuple(_key_lock._locks) == ('key1', 'key2')

    async def task2(_key_lock: KeyLock) -> None:
        await asyncio.sleep(.05)
        assert tuple(_key_lock._locks) == ('key1',)
        async with _key_lock.resource('key2'):
            assert tuple(_key_lock._locks) == ('key1', 'key2')
            await asyncio.sleep(.07)
            assert tuple(_key_lock._locks) == ('key2', 'key3')

    async def task3(_key_lock: KeyLock) -> None:
        await asyncio.sleep(.1)
        assert tuple(_key_lock._locks) == ('key2',)
        async with _key_lock.resource('key3'):
            assert tuple(_key_lock._locks) == ('key2', 'key3')
            lock2 = ref(_key_lock._locks['key2'])
            async with _key_lock.resource('key2'):
                assert tuple(_key_lock._locks) == ('key2', 'key3')
                assert lock2() is _key_lock._locks['key2']
                await asyncio.sleep(.1)
            assert lock2() is None
            assert tuple(_key_lock._locks) == ('key3',)

    key_lock = KeyLock()
    await asyncio.gather(
        task1(key_lock),
        task2(key_lock),
        task3(key_lock)
    )
