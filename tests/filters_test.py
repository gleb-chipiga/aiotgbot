import re
from dataclasses import dataclass
from typing import Any, Callable

import msgspec
import pytest
import pytest_asyncio

from aiotgbot import Bot, FilterProtocol, HandlerTable
from aiotgbot.api_types import CallbackQuery, Message, Update
from aiotgbot.bot import PollBot
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import ContentType, UpdateType
from aiotgbot.filters import (
    ANDFilter,
    CallbackQueryDataFilter,
    CommandsFilter,
    ContentTypeFilter,
    GroupChatFilter,
    MessageTextFilter,
    ORFilter,
    PrivateChatFilter,
    StateFilter,
    UpdateTypeFilter,
)
from aiotgbot.storage_memory import MemoryStorage


@pytest_asyncio.fixture
async def _bot() -> Bot:
    table = HandlerTable()
    table.freeze()
    return PollBot("token", table, MemoryStorage())


_MakeMessage = Callable[..., Message]


@pytest.fixture
def make_message() -> _MakeMessage:
    def _make_message(**kwargs: Any) -> Message:
        return msgspec.convert(
            {
                "message_id": 1,
                "date": 1,
                "chat": {"id": 1, "type": "private"},
                **kwargs,
            },
            Message,
        )

    return _make_message


_MakeBotUpdate = Callable[..., BotUpdate]


@pytest.fixture
def make_bot_update() -> _MakeBotUpdate:
    def _make_bot_update(
        state: str | None, context: Context, update_id: int = 1, **params: Any
    ) -> BotUpdate:
        params = {
            "message": None,
            "edited_message": None,
            "channel_post": None,
            "edited_channel_post": None,
            "inline_query": None,
            "chosen_inline_result": None,
            "callback_query": None,
            "shipping_query": None,
            "pre_checkout_query": None,
            "poll": None,
            "poll_answer": None,
            **params,
        }
        return BotUpdate(state, context, Update(update_id=update_id, **params))

    return _make_bot_update


def test_update_type_filter_protocol() -> None:
    _filter: FilterProtocol = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_update_type_filter(
    _bot: Bot, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert await _filter.check(
        _bot, make_bot_update(None, Context({}), channel_post={})
    )
    assert not await _filter.check(
        _bot, make_bot_update(None, Context({}), update_id=1)
    )


def test_state_filter_protocol() -> None:
    _filter: FilterProtocol = StateFilter("state1")
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_state_filter(
    _bot: Bot, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = StateFilter("state1")
    assert await _filter.check(_bot, make_bot_update("state1", Context({})))
    assert not await _filter.check(
        _bot, make_bot_update("state2", Context({}))
    )


def test_commands_filter_protocol() -> None:
    _filter: FilterProtocol = CommandsFilter(("command1",))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_commands_filter(
    _bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = CommandsFilter(("command1",))
    assert await _filter.check(
        _bot,
        make_bot_update(
            None, Context({}), message=make_message(text="/command1")
        ),
    )
    assert not await _filter.check(
        _bot,
        make_bot_update(
            None, Context({}), message=make_message(text="/command2")
        ),
    )
    assert not await _filter.check(_bot, make_bot_update(None, Context({})))


def test_content_types_filter_protocol() -> None:
    _filter: FilterProtocol = ContentTypeFilter((ContentType.TEXT,))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_content_types_filter_false(
    _bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = ContentTypeFilter((ContentType.TEXT,))
    assert not await _filter.check(_bot, make_bot_update(None, Context({})))
    assert not await _filter.check(
        _bot,
        make_bot_update(None, Context({}), message=make_message(photo=[])),
    )


@pytest.mark.parametrize(
    "payload",
    ("message", "edited_message", "channel_post", "edited_channel_post"),
)
@pytest.mark.asyncio
async def test_content_types_filter(
    _bot: Bot,
    make_message: _MakeMessage,
    make_bot_update: _MakeBotUpdate,
    payload: str,
) -> None:
    _filter = ContentTypeFilter((ContentType.TEXT,))
    assert await _filter.check(
        _bot,
        make_bot_update(
            None, Context({}), **{payload: make_message(text="text1")}
        ),
    )


def test_message_text_filter_protocol() -> None:
    _filter: FilterProtocol = MessageTextFilter(re.compile(r"\d{2}\.\d{2}"))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_message_text_filter(
    _bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = MessageTextFilter(re.compile(r"\d{2}\.\d{2}"))
    assert await _filter.check(
        _bot,
        make_bot_update(None, Context({}), message=make_message(text="01.02")),
    )
    assert not await _filter.check(
        _bot, make_bot_update(None, Context({}), message=make_message())
    )


def test_callback_query_data_filter_protocol() -> None:
    _filter: FilterProtocol = CallbackQueryDataFilter(
        re.compile(r"\d{2}\.\d{2}")
    )
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_callback_query_data_filter(
    _bot: Bot, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = CallbackQueryDataFilter(re.compile(r"\d{2}\.\d{2}"))
    user = {"id": 1, "is_bot": False, "first_name": "2"}
    cq = msgspec.convert(
        {"id": "1", "from": user, "data": "01.02", "chat_instance": "1"},
        CallbackQuery,
    )
    assert await _filter.check(
        _bot, make_bot_update(None, Context({}), callback_query=cq)
    )
    cq = msgspec.convert(
        {"id": "1", "from": user, "date": 1, "chat_instance": "1"},
        CallbackQuery,
    )
    assert not await _filter.check(
        _bot, make_bot_update(None, Context({}), callback_query=cq)
    )


def test_private_chat_filter_protocol() -> None:
    _filter: FilterProtocol = PrivateChatFilter()
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_private_chat_filter(
    _bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    _filter: FilterProtocol = PrivateChatFilter()
    assert await _filter.check(
        _bot, make_bot_update(None, Context({}), message=make_message())
    )
    assert not await _filter.check(
        _bot,
        make_bot_update(
            None,
            Context({}),
            message=make_message(chat={"id": 1, "type": "group"}),
        ),
    )


def test_group_chat_filter_protocol() -> None:
    _filter: FilterProtocol = GroupChatFilter()
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_group_chat_filter(
    _bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    _filter: FilterProtocol = GroupChatFilter()
    assert await _filter.check(
        _bot,
        make_bot_update(
            None,
            Context({}),
            message=make_message(chat={"id": 1, "type": "group"}),
        ),
    )
    assert not await _filter.check(
        _bot, make_bot_update(None, Context({}), message=make_message())
    )


@dataclass(frozen=True)
class FlagFilter(FilterProtocol):
    flag: bool

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return self.flag


@pytest.mark.parametrize(
    "flag1, flag2, result",
    (
        (False, True, True),
        (True, False, True),
        (True, True, True),
        (False, False, False),
    ),
)
@pytest.mark.asyncio
async def test_or_filter(
    _bot: Bot,
    make_bot_update: _MakeBotUpdate,
    flag1: bool,
    flag2: bool,
    result: bool,
) -> None:
    _filter: FilterProtocol = ORFilter(FlagFilter(flag1), FlagFilter(flag2))
    update = make_bot_update(None, Context({}))
    assert await _filter.check(_bot, update) == result


@pytest.mark.parametrize(
    "flag1, flag2, result",
    (
        (False, True, False),
        (True, False, False),
        (True, True, True),
        (False, False, False),
    ),
)
@pytest.mark.asyncio
async def test_and_filter(
    _bot: Bot,
    make_bot_update: _MakeBotUpdate,
    flag1: bool,
    flag2: bool,
    result: bool,
) -> None:
    _filter: FilterProtocol = ANDFilter(FlagFilter(flag1), FlagFilter(flag2))
    update = make_bot_update(None, Context({}))
    assert await _filter.check(_bot, update) == result
