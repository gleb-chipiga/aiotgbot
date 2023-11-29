import msgspec
import pytest
import pytest_asyncio

from aiotgbot.api_types import Message, Update
from aiotgbot.bot import Bot, Handler, PollBot
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import UpdateType
from aiotgbot.filters import StateFilter, UpdateTypeFilter
from aiotgbot.handler_table import HandlerTable
from aiotgbot.storage_memory import MemoryStorage


@pytest_asyncio.fixture
async def _bot() -> Bot:
    table = HandlerTable()
    table.freeze()
    bot = PollBot("token", table, MemoryStorage())
    bot["key1"] = "str1"
    bot["key2"] = "str2"
    bot["key3"] = 4

    return bot


@pytest.mark.asyncio
async def test_bot_get_item(_bot: Bot) -> None:
    assert _bot["key2"] == "str2"
    assert _bot.get("key4") is None


@pytest.mark.asyncio
async def test_bot_set_item(_bot: Bot) -> None:
    _bot["key5"] = 6
    assert _bot["key5"] == 6


@pytest.mark.asyncio
async def test_bot_delitem(_bot: Bot) -> None:
    assert _bot["key3"] == 4
    del _bot["key3"]
    assert _bot.get("key3") is None


@pytest.mark.asyncio
async def test_bot_len(_bot: Bot) -> None:
    assert len(_bot) == 3
    _bot["key6"] = 7
    assert len(_bot) == 4


@pytest.mark.asyncio
async def test_bot_iter(_bot: Bot) -> None:
    assert tuple(_bot) == ("key1", "key2", "key3")


@pytest.mark.asyncio
async def test_bot_storage(_bot: Bot) -> None:
    assert isinstance(_bot.storage, MemoryStorage)


@pytest.mark.asyncio
async def test_handler_check() -> None:
    async def func1(_: Bot, __: BotUpdate) -> None:
        ...

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
