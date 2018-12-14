import pytest

from aiotgbot import Bot, HandlerTable
from aiotgbot.api_types import CallbackQuery, Message, Update
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import ContentType, UpdateType
from aiotgbot.filters import (CallbackQueryDataFilter, CommandsFilter,
                              ContentTypeFilter, GroupChatFilter,
                              MessageTextFilter, PrivateChatFilter,
                              StateFilter, UpdateTypeFilter)
from aiotgbot.storage_memory import MemoryStorage


@pytest.fixture
def bot():
    return Bot('token', HandlerTable(), MemoryStorage())


@pytest.fixture
def make_msg():
    def _make_msg(**params):
        return Message.from_dict({
            'message_id': 1,
            'date': 1,
            'chat': {'id': 1, 'type': 'private'},
            **params
        })

    return _make_msg


@pytest.fixture
def make_bot_update():
    def _make_bot_update(state, context, update_id=1, **params):
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
            **params
        }
        return BotUpdate(state, context, Update(update_id, **params))

    return _make_bot_update


@pytest.mark.asyncio
async def test_update_type_filter(bot, make_bot_update):
    _filter = UpdateTypeFilter(UpdateType.CHANNEL_POST)
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), channel_post={}))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), update_id=1))


@pytest.mark.asyncio
async def test_state_filter(bot, make_bot_update):
    _filter = StateFilter('state1')
    assert await _filter.check(bot, make_bot_update('state1', Context({})))
    assert not await _filter.check(bot, make_bot_update('state2', Context({})))


@pytest.mark.asyncio
async def test_commands_filter(bot, make_msg, make_bot_update):
    _filter = CommandsFilter(('command1',))
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_msg(text='/command1')))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_msg(text='/command2')))
    assert not await _filter.check(bot, make_bot_update(None, Context({})))


@pytest.mark.asyncio
async def test_content_types_filter_false(bot, make_msg, make_bot_update):
    _filter = ContentTypeFilter((ContentType.TEXT,))
    assert not await _filter.check(bot, make_bot_update(None, Context({})))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_msg(photo=[])))


@pytest.mark.parametrize('payload', (
    'message',
    'edited_message',
    'channel_post',
    'edited_channel_post'
))
@pytest.mark.asyncio
async def test_content_types_filter(bot, make_msg, make_bot_update, payload):
    _filter = ContentTypeFilter((ContentType.TEXT,))
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), **{payload: make_msg(text='text1')}))


@pytest.mark.asyncio
async def test_message_text_filter(bot, make_msg, make_bot_update):
    _filter = MessageTextFilter(r'\d{2}\.\d{2}')
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_msg(text='01.02')))
    assert not await _filter.check(bot, make_bot_update(None, Context({}),
                                                        message=make_msg()))


@pytest.mark.asyncio
async def test_callback_query_data_filter(bot, make_bot_update):
    _filter = CallbackQueryDataFilter(r'\d{2}\.\d{2}')
    user = {'id': 1, 'is_bot': False, 'first_name': '2'}
    cq = CallbackQuery.from_dict({'id': '1', 'from': user, 'data': '01.02',
                                  'chat_instance': '1'})
    assert await _filter.check(bot, make_bot_update(None, Context({}),
                                                    callback_query=cq))
    cq = CallbackQuery.from_dict({'id': '1', 'from': user, 'date': 1,
                                  'chat_instance': '1'})
    assert not await _filter.check(bot, make_bot_update(None, Context({}),
                                                        callback_query=cq))


@pytest.mark.asyncio
async def test_private_chat_filter(bot, make_msg, make_bot_update):
    _filter = PrivateChatFilter()
    assert await _filter.check(bot, make_bot_update(None, Context({}),
                                                    message=make_msg()))
    assert not await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_msg(chat={'id': 1, 'type': 'group'})))


@pytest.mark.asyncio
async def test_group_chat_filter(bot, make_msg, make_bot_update):
    _filter = GroupChatFilter()
    assert await _filter.check(bot, make_bot_update(
        None, Context({}), message=make_msg(chat={'id': 1, 'type': 'group'})))
    assert not await _filter.check(bot, make_bot_update(None, Context({}),
                                                        message=make_msg()))
