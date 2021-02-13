import asyncio
from typing import AsyncIterator, cast

import aiotgbot.runner
import pytest
from aiotgbot import Runner


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
        Runner(cast(aiotgbot.runner.ContextFunction, _context))


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
