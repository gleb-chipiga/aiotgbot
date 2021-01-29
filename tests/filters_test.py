import re
from typing import Any, Callable, Optional

import pytest

from aiotgbot import Bot, FilterProtocol, HandlerTable
from aiotgbot.api_types import CallbackQuery, Message, Update
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import ContentType, UpdateType
from aiotgbot.filters import (CallbackQueryDataFilter, CommandsFilter,
                              ContentTypeFilter, GroupChatFilter,
                              MessageTextFilter, PrivateChatFilter,
                              StateFilter, UpdateTypeFilter)
from aiotgbot.storage_memory import MemoryStorage


@pytest.fixture
def bot() -> Bot:
    return Bot('token', HandlerTable(), MemoryStorage())


_MakeMessage = Callable[..., Message]


@pytest.fixture
def make_message() -> _MakeMessage:
    def _make_message(**kwargs: Any) -> Message:
        return Message.from_dict({
            'message_id': 1,
            'date': 1,
            'chat': {'id': 1, 'type': 'private'},
            **kwargs
        })
    return _make_message


_MakeBotUpdate = Callable[..., BotUpdate]


@pytest.fixture
def make_bot_update() -> _MakeBotUpdate:
    def _make_bot_update(state: Optional[str], context: Context,
                         update_id: int = 1, **params: Any) -> BotUpdate:
        params = {
            'message': None,
            'edited_message': None,
            'channel_post': None,
            'edited_channel_post': None,
            'inline_query': None,
            'chosen_inline_result': None,
            'callback_query': None,
            'shipping_query': None,
            'pre_checkout_query': None,
            'poll': None,
            'poll_answer': None,
            **params
        }
        return BotUpdate(state, context, Update(update_id, **params))
    return _make_bot_update


def test_update_type_filter_protocol() -> None:
    _filter: FilterProtocol = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_update_type_filter(
    bot: Bot, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), channel_post={}))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), update_id=1))


def test_state_filter_protocol() -> None:
    _filter: FilterProtocol = StateFilter('state1')
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_state_filter(bot: Bot, make_bot_update: _MakeBotUpdate) -> None:
    _filter = StateFilter('state1')
    assert await _filter.check(bot, make_bot_update('state1', Context({})))
    assert not await _filter.check(bot, make_bot_update('state2', Context({})))


def test_commands_filter_protocol() -> None:
    _filter: FilterProtocol = CommandsFilter(('command1',))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_commands_filter(bot: Bot, make_message: _MakeMessage,
                               make_bot_update: _MakeBotUpdate) -> None:
    _filter = CommandsFilter(('command1',))
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_message(text='/command1')))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_message(text='/command2')))
    assert not await _filter.check(bot, make_bot_update(None, Context({})))


def test_content_types_filter_protocol() -> None:
    _filter: FilterProtocol = ContentTypeFilter((ContentType.TEXT,))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_content_types_filter_false(
    bot: Bot, make_message: _MakeMessage, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = ContentTypeFilter((ContentType.TEXT,))
    assert not await _filter.check(bot, make_bot_update(None, Context({})))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_message(photo=[])))


@pytest.mark.parametrize('payload', (
    'message',
    'edited_message',
    'channel_post',
    'edited_channel_post'
))
@pytest.mark.asyncio
async def test_content_types_filter(bot: Bot, make_message: _MakeMessage,
                                    make_bot_update: _MakeBotUpdate,
                                    payload: str) -> None:
    _filter = ContentTypeFilter((ContentType.TEXT,))
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), **{payload: make_message(text='text1')}))


def test_message_text_filter_protocol() -> None:
    _filter: FilterProtocol = MessageTextFilter(re.compile(r'\d{2}\.\d{2}'))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_message_text_filter(bot: Bot, make_message: _MakeMessage,
                                   make_bot_update: _MakeBotUpdate) -> None:
    _filter = MessageTextFilter(re.compile(r'\d{2}\.\d{2}'))
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_message(text='01.02')))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_message()))


def test_callback_query_data_filter_protocol() -> None:
    _filter: FilterProtocol = CallbackQueryDataFilter(
        re.compile(r'\d{2}\.\d{2}'))
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_callback_query_data_filter(
    bot: Bot, make_bot_update: _MakeBotUpdate
) -> None:
    _filter = CallbackQueryDataFilter(re.compile(r'\d{2}\.\d{2}'))
    user = {'id': 1, 'is_bot': False, 'first_name': '2'}
    cq = CallbackQuery.from_dict({'id': '1', 'from': user, 'data': '01.02',
                                  'chat_instance': '1'})
    assert await _filter.check(bot, make_bot_update(None, Context({}),
                                                    callback_query=cq))
    cq = CallbackQuery.from_dict({'id': '1', 'from': user, 'date': 1,
                                  'chat_instance': '1'})
    assert not await _filter.check(bot, make_bot_update(None, Context({}),
                                                        callback_query=cq))


def test_private_chat_filter_protocol() -> None:
    _filter: FilterProtocol = PrivateChatFilter()
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_private_chat_filter(bot: Bot, make_message: _MakeMessage,
                                   make_bot_update: _MakeBotUpdate) -> None:
    _filter: FilterProtocol = PrivateChatFilter()
    assert await _filter.check(bot, make_bot_update(None, Context({}),
                                                    message=make_message()))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}),
        message=make_message(chat={'id': 1, 'type': 'group'})))


def test_group_chat_filter_protocol() -> None:
    _filter: FilterProtocol = GroupChatFilter()
    assert isinstance(_filter, FilterProtocol)


@pytest.mark.asyncio
async def test_group_chat_filter(bot: Bot, make_message: _MakeMessage,
                                 make_bot_update: _MakeBotUpdate) -> None:
    _filter: FilterProtocol = GroupChatFilter()
    assert await _filter.check(bot, make_bot_update(
        None, Context({}),
        message=make_message(chat={'id': 1, 'type': 'group'})))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_message()))
