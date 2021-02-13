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
    async def context(runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, runner.stop)
        yield

    Runner(context).run()


def test_runner_signal_handler() -> None:
    async def context(runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, runner._signal_handler,
                                              'SIGINT')
        yield

    Runner(context).run()


def test_runner_context_type_error() -> None:
    async def context(_: Runner) -> None:
        return None

    with pytest.raises(RuntimeError, match='Argument is not async generator'):
        Runner(cast(aiotgbot.runner.ContextFunction, context))


def test_runner_context_multiple_yield_error() -> None:
    async def context(runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, runner.stop)
        yield
        yield

    with pytest.raises(RuntimeError, match='has more than one \'yield\''):
        Runner(context).run()


def test_runner_context_started_error() -> None:
    async def context(runner: Runner) -> AsyncIterator[None]:
        with pytest.raises(RuntimeError, match='Already started'):
            runner.run()
        asyncio.get_running_loop().call_later(.01, runner.stop)
        yield

    Runner(context).run()


def test_runner_context_stop_started_error() -> None:
    async def context(_runner: Runner) -> AsyncIterator[None]:
        yield

    runner = Runner(context)
    with pytest.raises(RuntimeError, match='Not started'):
        runner.stop()


def test_runner_context_stop_stopped_error() -> None:
    async def context(_runner: Runner) -> AsyncIterator[None]:
        asyncio.get_running_loop().call_later(.01, _runner.stop)
        yield

    runner = Runner(context)
    runner.run()
    with pytest.raises(RuntimeError, match='Already stopped'):
        runner.stop()
