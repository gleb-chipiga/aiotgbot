import asyncio
from typing import assert_type

import msgspec
import pytest
import pytest_asyncio

from aiotgbot.api_types import Message, Update
from aiotgbot.bot import Bot, Handler, PollBot, StorageKey
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import UpdateType
from aiotgbot.filters import StateFilter, UpdateTypeFilter
from aiotgbot.handler_table import HandlerTable
from aiotgbot.helpers import BotKey
from aiotgbot.storage_memory import MemoryStorage


@pytest_asyncio.fixture
async def bot() -> Bot:
    table = HandlerTable()
    table.freeze()
    bot = PollBot("token", table, MemoryStorage())
    bot["key1"] = "str1"
    bot["key2"] = "str2"
    bot["key3"] = 4
    await asyncio.sleep(0)
    return bot


def test_bot_get_item(bot: Bot) -> None:
    assert bot["key2"] == "str2"
    assert bot.get("key4") is None


def test_bot_set_item(bot: Bot) -> None:
    bot["key5"] = 6
    assert bot["key5"] == 6


def test_bot_delitem(bot: Bot) -> None:
    assert bot["key3"] == 4
    del bot["key3"]
    assert bot.get("key3") is None


def test_bot_len(bot: Bot) -> None:
    assert len(bot) == 3
    bot["key6"] = 7
    assert len(bot) == 4


def test_bot_iter(bot: Bot) -> None:
    assert tuple(bot) == ("key1", "key2", "key3")


def test_bot_iter_preserves_typed_keys(bot: Bot) -> None:
    typed_key: BotKey[int] = BotKey("typed-key", int)
    bot[typed_key] = 42
    keys = tuple(bot)
    assert typed_key in keys
    _ = assert_type(keys, tuple[StorageKey, ...])


def test_bot_storage(bot: Bot) -> None:
    assert isinstance(bot.storage, MemoryStorage)


@pytest.mark.asyncio
async def test_handler_check() -> None:
    async def func1(_: Bot, _update: BotUpdate) -> None: ...

    handler = Handler(
        func1,
        (
            UpdateTypeFilter(UpdateType.MESSAGE),
            StateFilter("state1"),
        ),
    )

    table = HandlerTable()
    table.freeze()
    bot = PollBot("token", table, MemoryStorage())
    ctx = Context({"key1": "str1", "key2": "str2", "key3": 4})
    message = msgspec.convert(
        {"message_id": 1, "date": 1, "chat": {"id": 1, "type": "private"}},
        Message,
    )
    bu1 = BotUpdate("state1", ctx, Update(update_id=1, message=message))
    assert await handler.check(bot, bu1)
    bu2 = BotUpdate("state2", ctx, Update(update_id=2, message=message))
    assert not await handler.check(bot, bu2)
