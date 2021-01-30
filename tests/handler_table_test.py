import re

import pytest

from aiotgbot.api_types import Message, Update
from aiotgbot.bot import Bot, Handler, HandlerCallable, HandlerTableProtocol
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.constants import ContentType, UpdateType
from aiotgbot.filters import (CallbackQueryDataFilter, CommandsFilter,
                              ContentTypeFilter, GroupChatFilter,
                              MessageTextFilter, PrivateChatFilter,
                              StateFilter, UpdateTypeFilter)
from aiotgbot.handler_table import HandlerTable
from aiotgbot.storage_memory import MemoryStorage


@pytest.fixture
def handler() -> HandlerCallable:
    async def _handler(_: Bot, __: BotUpdate) -> None: ...

    return _handler


def test_handler_table_protocol() -> None:
    ht: HandlerTableProtocol = HandlerTable()
    assert isinstance(ht, HandlerTableProtocol)


def test_freeze(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    assert not ht.frozen
    ht.message_handler(handler, state='state1', commands=['command1'],
                       content_types=[ContentType.CONTACT],
                       text_match='pattern',
                       filters=[PrivateChatFilter()])
    ht.freeze()
    assert ht.frozen
    with pytest.raises(RuntimeError, match='Cannot modify frozen list.'):
        ht.message_handler(handler, state='state1', commands=['command1'],
                           content_types=[ContentType.CONTACT],
                           text_match='pattern',
                           filters=[PrivateChatFilter()])


def test_handler_table_message_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()

    ht.message_handler(handler, state='state1', commands=['command1'],
                       content_types=[ContentType.CONTACT],
                       text_match=re.compile('pattern'),
                       filters=[PrivateChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.MESSAGE),
        StateFilter('state1'),
        CommandsFilter(('command1',)),
        ContentTypeFilter((ContentType.CONTACT,)),
        MessageTextFilter(re.compile('pattern')),
        PrivateChatFilter()
    ))]


def test_handler_table_message(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.message(state='state1', commands=['command1'],
               content_types=[ContentType.CONTACT],
               text_match='pattern',
               filters=[PrivateChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.MESSAGE),
        StateFilter('state1'),
        CommandsFilter(('command1',)),
        ContentTypeFilter((ContentType.CONTACT,)),
        MessageTextFilter(re.compile('pattern')),
        PrivateChatFilter()
    ))]


def test_handler_table_edited_message_handler(
    handler: HandlerCallable
) -> None:
    ht = HandlerTable()
    ht.edited_message_handler(handler,
                              state='state1',
                              filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.EDITED_MESSAGE),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_edited_message(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.edited_message(state='state1',
                      filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.EDITED_MESSAGE),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_channel_post_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.channel_post_handler(handler,
                            state='state1',
                            filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_channel_post(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.channel_post(state='state1',
                    filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_edited_channel_post_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.edited_channel_post_handler(handler,
                                   state='state1',
                                   filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.EDITED_CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_edited_channel_post(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.edited_channel_post(state='state1',
                           filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.EDITED_CHANNEL_POST),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_inline_query_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.inline_query_handler(handler,
                            state='state1',
                            filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.INLINE_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_table_inline_query(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.inline_query(state='state1',
                    filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.INLINE_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_chosen_inline_result_handler(
    handler: HandlerCallable
) -> None:
    ht = HandlerTable()
    ht.chosen_inline_result_handler(handler,
                                    state='state1',
                                    filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.CHOSEN_INLINE_RESULT),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_chosen_inline_result(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.chosen_inline_result(state='state1',
                            filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.CHOSEN_INLINE_RESULT),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_callback_query_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.callback_query_handler(handler,
                              state='state1',
                              data_match=re.compile('pattern'),
                              filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.CALLBACK_QUERY),
        StateFilter('state1'),
        CallbackQueryDataFilter(re.compile('pattern')),
        GroupChatFilter()
    ))]


def test_handler_callback_query(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.callback_query(state='state1',
                      data_match='pattern',
                      filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.CALLBACK_QUERY),
        StateFilter('state1'),
        CallbackQueryDataFilter(re.compile('pattern')),
        GroupChatFilter()
    ))]


def test_handler_shipping_query_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.shipping_query_handler(handler,
                              state='state1',
                              filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.SHIPPING_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_shipping_query(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.shipping_query(state='state1',
                      filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.SHIPPING_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_pre_checkout_query_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.pre_checkout_query_handler(handler,
                                  state='state1',
                                  filters=[GroupChatFilter()])

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.PRE_CHECKOUT_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


def test_handler_pre_checkout_query(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.pre_checkout_query(state='state1',
                          filters=[GroupChatFilter()])(handler)

    assert ht._handlers == [Handler(handler, filters=(
        UpdateTypeFilter(UpdateType.PRE_CHECKOUT_QUERY),
        StateFilter('state1'),
        GroupChatFilter()
    ))]


@pytest.mark.asyncio
async def test_handler_get_handler(handler: HandlerCallable) -> None:
    ht = HandlerTable()
    ht.message(state='state1')(handler)
    _bot = Bot('token', HandlerTable(), MemoryStorage())
    ctx = Context({'key1': 'str1', 'key2': 'str2', 'key3': 4})
    message = Message.from_dict({'message_id': 1, 'date': 1,
                                 'chat': {'id': 1, 'type': 'private'}})
    bu1 = BotUpdate('state1', ctx, Update(update_id=1, message=message))
    assert await ht.get_handler(_bot, bu1) == handler
    bu2 = BotUpdate('state2', ctx, Update(update_id=2, message=message))
    assert await ht.get_handler(_bot, bu2) is None
