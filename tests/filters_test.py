import asyncio
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict, Unpack

import msgspec
import pytest
import pytest_asyncio
from typing_extensions import override  # Python 3.11 compatibility

from aiotgbot import Bot, FilterProtocol, HandlerTable
from aiotgbot.api_types import (
    CallbackQuery,
    ChatJoinRequest,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    MessageReactionCountUpdated,
    MessageReactionUpdated,
    Poll,
    PollAnswer,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
)
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
    NOTFilter,
    ORFilter,
    PrivateChatFilter,
    StateFilter,
    UpdateTypeFilter,
)
from aiotgbot.storage_memory import MemoryStorage


@pytest_asyncio.fixture
async def bot() -> Bot:
    table = HandlerTable()
    table.freeze()
    bot = PollBot("token", table, MemoryStorage())
    await asyncio.sleep(0)
    return bot


_MakeMessage = Callable[..., Message]


@pytest.fixture
def make_message() -> _MakeMessage:
    def _make_message(**kwargs: object) -> Message:
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


class _UpdateParams(TypedDict, total=False):
    message: Message
    edited_message: Message
    channel_post: Message
    edited_channel_post: Message
    message_reaction: MessageReactionUpdated
    message_reaction_count: MessageReactionCountUpdated
    inline_query: InlineQuery
    chosen_inline_result: ChosenInlineResult
    callback_query: CallbackQuery
    shipping_query: ShippingQuery
    pre_checkout_query: PreCheckoutQuery
    poll: Poll
    poll_answer: PollAnswer
    my_chat_member: ChatMemberUpdated
    chat_member: ChatMemberUpdated
    chat_join_request: ChatJoinRequest


@pytest.fixture
def make_bot_update() -> _MakeBotUpdate:
    def _make_bot_update(
        state: str | None,
        context: Context,
        update_id: int = 1,
        **params: Unpack[_UpdateParams],
    ) -> BotUpdate:
        return BotUpdate(
            state,
            context,
            Update(update_id=update_id, **params),
        )

    return _make_bot_update


def test_update_type_filter_protocol() -> None:
    filter_: FilterProtocol = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_update_type_filter(
    bot: Bot, make_bot_update: _MakeBotUpdate, make_message: _MakeMessage
) -> None:
    filter_ = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert await filter_.check(
        bot, make_bot_update(None, Context({}), channel_post=make_message())
    )
    assert not await filter_.check(bot, make_bot_update(None, Context({}), update_id=1))


def test_state_filter_protocol() -> None:
    filter_: FilterProtocol = StateFilter("state1")
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_state_filter(bot: Bot, make_bot_update: _MakeBotUpdate) -> None:
    filter_ = StateFilter("state1")
    assert await filter_.check(bot, make_bot_update("state1", Context({})))
    assert not await filter_.check(bot, make_bot_update("state2", Context({})))


def test_commands_filter_protocol() -> None:
    filter_: FilterProtocol = CommandsFilter(("command1",))
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_commands_filter(
    bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    filter_ = CommandsFilter(("command1",))
    assert await filter_.check(
        bot,
        make_bot_update(None, Context({}), message=make_message(text="/command1")),
    )
    assert not await filter_.check(
        bot,
        make_bot_update(None, Context({}), message=make_message(text="/command2")),
    )
    assert not await filter_.check(bot, make_bot_update(None, Context({})))


def test_content_types_filter_protocol() -> None:
    filter_: FilterProtocol = ContentTypeFilter((ContentType.TEXT,))
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_content_types_filter_false(
    bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    filter_ = ContentTypeFilter((ContentType.TEXT,))
    assert not await filter_.check(bot, make_bot_update(None, Context({})))
    assert not await filter_.check(
        bot,
        make_bot_update(None, Context({}), message=make_message(photo=[])),
    )


@pytest.mark.parametrize(
    "payload",
    ("message", "edited_message", "channel_post", "edited_channel_post"),
)
@pytest.mark.asyncio
async def test_content_types_filter(
    bot: Bot,
    make_message: _MakeMessage,
    make_bot_update: _MakeBotUpdate,
    payload: str,
) -> None:
    filter_ = ContentTypeFilter((ContentType.TEXT,))
    assert await filter_.check(
        bot,
        make_bot_update(None, Context({}), **{payload: make_message(text="text1")}),
    )


def test_message_text_filter_protocol() -> None:
    filter_: FilterProtocol = MessageTextFilter(re.compile(r"\d{2}\.\d{2}"))
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_message_text_filter(
    bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    filter_ = MessageTextFilter(re.compile(r"\d{2}\.\d{2}"))
    assert await filter_.check(
        bot,
        make_bot_update(None, Context({}), message=make_message(text="01.02")),
    )
    assert not await filter_.check(
        bot, make_bot_update(None, Context({}), message=make_message())
    )


def test_callback_query_data_filter_protocol() -> None:
    filter_: FilterProtocol = CallbackQueryDataFilter(re.compile(r"\d{2}\.\d{2}"))
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_callback_query_data_filter(
    bot: Bot, make_bot_update: _MakeBotUpdate
) -> None:
    filter_ = CallbackQueryDataFilter(re.compile(r"\d{2}\.\d{2}"))
    user = {"id": 1, "is_bot": False, "first_name": "2"}
    cq = msgspec.convert(
        {"id": "1", "from": user, "data": "01.02", "chat_instance": "1"},
        CallbackQuery,
    )
    assert await filter_.check(
        bot, make_bot_update(None, Context({}), callback_query=cq)
    )
    cq = msgspec.convert(
        {"id": "1", "from": user, "date": 1, "chat_instance": "1"},
        CallbackQuery,
    )
    assert not await filter_.check(
        bot, make_bot_update(None, Context({}), callback_query=cq)
    )


def test_private_chat_filter_protocol() -> None:
    filter_: FilterProtocol = PrivateChatFilter()
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_private_chat_filter(
    bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    filter_: FilterProtocol = PrivateChatFilter()
    assert await filter_.check(
        bot, make_bot_update(None, Context({}), message=make_message())
    )
    assert not await filter_.check(
        bot,
        make_bot_update(
            None,
            Context({}),
            message=make_message(chat={"id": 1, "type": "group"}),
        ),
    )


def test_group_chat_filter_protocol() -> None:
    filter_: FilterProtocol = GroupChatFilter()
    assert isinstance(filter_, FilterProtocol)


@pytest.mark.asyncio
async def test_group_chat_filter(
    bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    filter_: FilterProtocol = GroupChatFilter()
    assert await filter_.check(
        bot,
        make_bot_update(
            None,
            Context({}),
            message=make_message(chat={"id": 1, "type": "group"}),
        ),
    )
    assert not await filter_.check(
        bot, make_bot_update(None, Context({}), message=make_message())
    )


@dataclass(frozen=True)
class FlagFilter(FilterProtocol):
    flag: bool

    @override
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
    bot: Bot,
    make_bot_update: _MakeBotUpdate,
    flag1: bool,
    flag2: bool,
    result: bool,
) -> None:
    filter_: FilterProtocol = ORFilter(FlagFilter(flag1), FlagFilter(flag2))
    update = make_bot_update(None, Context({}))
    assert await filter_.check(bot, update) == result


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
    bot: Bot,
    make_bot_update: _MakeBotUpdate,
    flag1: bool,
    flag2: bool,
    result: bool,
) -> None:
    filter_: FilterProtocol = ANDFilter(FlagFilter(flag1), FlagFilter(flag2))
    update = make_bot_update(None, Context({}))
    assert await filter_.check(bot, update) == result


@pytest.mark.parametrize(
    "flag, result",
    (
        (False, True),
        (True, False),
    ),
)
@pytest.mark.asyncio
async def test_not_filter(
    bot: Bot,
    make_bot_update: _MakeBotUpdate,
    flag: bool,
    result: bool,
) -> None:
    filter_: FilterProtocol = NOTFilter(FlagFilter(flag))
    update = make_bot_update(None, Context({}))
    assert await filter_.check(bot, update) == result
