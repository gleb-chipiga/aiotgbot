import asyncio
from collections.abc import Hashable
from weakref import ref

import pytest

from aiotgbot.helpers import KeyLock


class InspectableKeyLock(KeyLock):
    def lock_order(self) -> tuple[Hashable, ...]:
        return tuple(self._locks)

    def lock_keys(self) -> tuple[Hashable, ...]:
        return tuple(self._locks.keys())

    def get_lock(self, key: Hashable) -> asyncio.Lock:
        return self._locks[key]


@pytest.mark.asyncio
async def test_sleep() -> None:
    loop = asyncio.get_running_loop()
    time1 = loop.time()
    await asyncio.sleep(0.1)
    time2 = loop.time()

    assert 0.09 < time2 - time1 < 0.11


@pytest.mark.asyncio
async def test_key_lock_intervals() -> None:
    key_lock = InspectableKeyLock()
    loop = asyncio.get_running_loop()

    async def lock(_key_lock: KeyLock) -> tuple[float, float, float]:
        time1 = loop.time()
        async with _key_lock.resource("key"):
            time2 = loop.time()
            await asyncio.sleep(0.1)
            time3 = loop.time()
        return time2, time3, time2 - time1

    tasks = (lock(key_lock), lock(key_lock), lock(key_lock))
    intervals = list(await asyncio.gather(*tasks))
    intervals.sort(key=lambda i: i[0])
    assert intervals[0][2] < 0.01
    assert 0.09 < intervals[1][2] < 0.11
    assert 0.11 < intervals[2][2] < 0.21
    assert intervals[0][1] < intervals[1][0]
    assert intervals[1][1] < intervals[2][0]

    assert key_lock.lock_order() == ()


@pytest.mark.asyncio
async def test_key_lock_keys() -> None:
    key_lock = InspectableKeyLock()
    assert key_lock.lock_order() == ()
    async with key_lock.resource("key2"):
        assert key_lock.lock_keys() == ("key2",)
        async with key_lock.resource("key3"):
            assert key_lock.lock_keys() == ("key2", "key3")
            async with key_lock.resource("key4"):
                assert key_lock.lock_keys() == (
                    "key2",
                    "key3",
                    "key4",
                )
        assert key_lock.lock_keys() == ("key2",)
    assert key_lock.lock_order() == ()


@pytest.mark.asyncio
async def test_key_lock_overlaps() -> None:
    async def task1(_key_lock: InspectableKeyLock) -> None:
        async with _key_lock.resource("key1"):
            assert _key_lock.lock_order() == ("key1",)
            await asyncio.sleep(0.1)
            assert _key_lock.lock_order() == ("key1", "key2")

    async def task2(_key_lock: InspectableKeyLock) -> None:
        await asyncio.sleep(0.05)
        assert _key_lock.lock_order() == ("key1",)
        async with _key_lock.resource("key2"):
            assert _key_lock.lock_order() == ("key1", "key2")
            await asyncio.sleep(0.07)
            assert _key_lock.lock_order() == ("key2", "key3")

    async def task3(_key_lock: InspectableKeyLock) -> None:
        await asyncio.sleep(0.1)
        assert _key_lock.lock_order() == ("key2",)
        async with _key_lock.resource("key3"):
            assert _key_lock.lock_order() == ("key2", "key3")
            lock2 = ref(_key_lock.get_lock("key2"))
            async with _key_lock.resource("key2"):
                assert _key_lock.lock_order() == ("key2", "key3")
                assert lock2() is _key_lock.get_lock("key2")
                await asyncio.sleep(0.1)
            assert lock2() is None
            assert _key_lock.lock_order() == ("key3",)

    key_lock = InspectableKeyLock()
    _ = await asyncio.gather(task1(key_lock), task2(key_lock), task3(key_lock))
