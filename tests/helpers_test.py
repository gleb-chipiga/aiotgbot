import asyncio
from typing import AsyncIterator, List, Tuple, cast

import pytest

from aiotgbot import helpers
from aiotgbot.helpers import KeyLock, Runner


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


def test_runner_mapping() -> None:
    async def _context(_runner: Runner) -> AsyncIterator[None]:
        yield

    runner = Runner(_context)
    runner['key1'] = 'value1'
    runner['key2'] = 'value2'
    assert runner['key1'] == 'value1'
    assert len(runner) == 2
    assert tuple(runner) == ('key1', 'key2')
    del runner['key1']
    assert tuple(runner) == ('key2',)


def test_runner() -> None:
    async def _context(_runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, _runner.stop)
        yield

    runner = Runner(_context)
    runner.run()


def test_runner_context_type_error() -> None:
    async def _context(_runner: Runner) -> None:
        return None

    with pytest.raises(RuntimeError, match='Argument is not async generator'):
        Runner(cast(helpers.ContextFunction, _context))


def test_runner_context_multiple_yield_error() -> None:
    async def _context(_runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, _runner.stop)
        yield
        yield

    with pytest.raises(RuntimeError, match='has more than one \'yield\''):
        runner = Runner(_context)
        runner.run()


def test_runner_context_started_error() -> None:
    async def _context(_runner: Runner) -> AsyncIterator[None]:
        with pytest.raises(RuntimeError, match='Already started'):
            _runner.run()
        asyncio.get_running_loop().call_later(.01, _runner.stop)
        yield

    runner = Runner(_context)
    runner.run()


def test_runner_context_stop_started_error() -> None:
    async def _context(_runner: Runner) -> AsyncIterator[None]:
        yield

    runner = Runner(_context)
    with pytest.raises(RuntimeError, match='Not started'):
        runner.stop()


def test_runner_context_stop_stopped_error() -> None:
    async def _context(_runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, _runner.stop)
        yield

    runner = Runner(_context)
    runner.run()
    with pytest.raises(RuntimeError, match='Already stopped'):
        runner.stop()
