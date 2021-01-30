import asyncio
from typing import List, Tuple, cast

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
async def test_key_lock() -> None:
    key_lock = KeyLock()
    loop = asyncio.get_running_loop()

    time_marks = Tuple[float, float, float]

    async def lock(_key_lock: KeyLock) -> time_marks:
        time1 = loop.time()
        async with _key_lock.acquire('test'):
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
