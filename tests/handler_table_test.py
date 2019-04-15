import pytest

from aiotgbot.api_types import Message, Update
from aiotgbot.bot import Bot, Handler
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import ContentType, UpdateType
from aiotgbot.filters import (CallbackQueryDataFilter, CommandsFilter,
                              ContentTypeFilter, GroupChatFilter,
                              MessageTextFilter, PrivateChatFilter,
                              StateFilter, UpdateTypeFilter)
from aiotgbot.handler_table import HandlerTable
from aiotgbot.storage_memory import MemoryStorage


def test_handler_table_handlers():
    ht = HandlerTable()
    assert ht._handlers == []


def test_handler_table_message_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.message_handler(func, state='state1', commands=['command1'],
                       content_types=[ContentType.CONTACT],
                       text_match='pattern',
                       filters=[PrivateChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.MESSAGE),
        StateFilter('state1'),
        CommandsFilter(('command1',)),
        ContentTypeFilter((ContentType.CONTACT,)),
        MessageTextFilter('pattern'),
        PrivateChatFilter()
    ))]


def test_handler_table_message():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.message(state='state1', commands=['command1'],
               content_types=[ContentType.CONTACT],
               text_match='pattern',
               filters=[PrivateChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.MESSAGE),
        StateFilter('state1'),
        CommandsFilter(('command1',)),
        ContentTypeFilter((ContentType.CONTACT,)),
        MessageTextFilter('pattern'),
        PrivateChatFilter()
    ))]


def test_handler_table_edited_message_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.edited_message_handler(func,
                              state='state1',
                              filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.EDITED_MESSAGE),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_edited_message():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.edited_message(state='state1',
                      filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.EDITED_MESSAGE),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_channel_post_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.channel_post_handler(func,
                            state='state1',
                            filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_channel_post():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.channel_post(state='state1',
                    filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_edited_channel_post_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.edited_channel_post_handler(func,
                                   state='state1',
                                   filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.EDITED_CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_edited_channel_post():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.edited_channel_post(state='state1',
                           filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.EDITED_CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_inline_query_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.inline_query_handler(func,
                            state='state1',
                            filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.INLINE_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_inline_query():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.inline_query(state='state1',
                    filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.INLINE_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_chosen_inline_result_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.chosen_inline_result_handler(func,
                                    state='state1',
                                    filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.CHOSEN_INLINE_RESULT),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_chosen_inline_result():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.chosen_inline_result(state='state1',
                            filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.CHOSEN_INLINE_RESULT),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_callback_query_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.callback_query_handler(func,
                              state='state1',
                              data_match='pattern',
                              filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.CALLBACK_QUERY),
        StateFilter('state1'),
        CallbackQueryDataFilter('pattern'),
        GroupChatFilter()
    ))]


def test_handler_callback_query():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.callback_query(state='state1',
                      data_match='pattern',
                      filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.CALLBACK_QUERY),
        StateFilter('state1'),
        CallbackQueryDataFilter('pattern'),
        GroupChatFilter()
    ))]


def test_handler_shipping_query_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.shipping_query_handler(func,
                              state='state1',
                              filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.SHIPPING_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_shipping_query():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.shipping_query(state='state1',
                      filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.SHIPPING_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_pre_checkout_query_handler():
    async def handler(bot, update): ...

    ht = HandlerTable()
    ht.pre_checkout_query_handler(handler,
                                  state='state1',
                                  filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.PRE_CHECKOUT_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_pre_checkout_query():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.pre_checkout_query(state='state1',
                          filters=[GroupChatFilter()])(func)

    assert ht._handlers == [Handler(func, filters=(
        UpdateTypeFilter(UpdateType.PRE_CHECKOUT_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


@pytest.mark.asyncio
async def test_handler_get_handler():
    async def func(bot, update): ...

    ht = HandlerTable()
    ht.message(state='state1')(func)
    _bot = Bot('token', HandlerTable(), MemoryStorage())
    ctx = Context({'key1': 'str1', 'key2': 'str2', 'key3': 4})
    params = {
        'message': Message.from_dict({'message_id': 1, 'date': 1,
                                      'chat': {'id': 1, 'type': 'private'}}),
        'edited_message': None,
        'channel_post': None,
        'edited_channel_post': None,
        'inline_query': None,
        'chosen_inline_result': None,
        'callback_query': None,
        'shipping_query': None,
        'pre_checkout_query': None,
        'poll': None
    }
    bu1 = BotUpdate('state1', ctx, Update(update_id=1, **params))
    assert await ht.get_handler(_bot, bu1) == func
    bu2 = BotUpdate('state2', ctx, Update(update_id=2, **params))
    assert await ht.get_handler(_bot, bu2) is None
