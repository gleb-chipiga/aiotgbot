from typing import Dict, Union

import pytest

from aiotgbot.api_types import (CallbackQuery, ChosenInlineResult, InlineQuery,
                                Message, PreCheckoutQuery, ShippingQuery,
                                Update)
from aiotgbot.bot_update import BotUpdate, Context


@pytest.fixture
def context() -> Context:
    return Context({'key1': 'str1', 'key2': 'str2', 'key3': 4})


@pytest.fixture
def message() -> Message:
    return Message.from_dict({'message_id': 1, 'date': 1,
                              'chat': {'id': 1, 'type': 'private'}})


@pytest.fixture
def update(message: Message) -> Update:
    return Update(update_id=1, message=message)


@pytest.fixture
def bot_update(context: Context, update: Update) -> BotUpdate:
    bu = BotUpdate(state='state1', context=context, update=update)
    bu['key1'] = 'str1'
    bu['key2'] = 'str2'
    bu['key3'] = 4
    return bu


_UserDict = Dict[str, Union[int, bool, str]]


@pytest.fixture
def user_dict() -> _UserDict:
    return {'id': 1, 'is_bot': False, 'first_name': '2'}


def test_context_init() -> None:
    ctx = Context({'1': 2})
    assert ctx.to_dict() == {'1': 2}


def test_context_get_item(context: Context) -> None:
    assert context['key2'] == 'str2'
    assert context.get('key4') is None


def test_context_set_item(context: Context) -> None:
    context['key5'] = 6
    assert context.to_dict() == {'key1': 'str1', 'key2': 'str2', 'key3': 4,
                                 'key5': 6}


def test_context_delitem(context: Context) -> None:
    del context['key3']
    assert context.to_dict() == {'key1': 'str1', 'key2': 'str2'}


def test_context_len(context: Context) -> None:
    assert len(context) == 3
    context['key6'] = 7
    assert len(context) == 4


def test_context_iter(context: Context) -> None:
    assert tuple(context) == ('key1', 'key2', 'key3')


def test_context_clear(context: Context) -> None:
    assert context.to_dict() == {'key1': 'str1', 'key2': 'str2', 'key3': 4}
    context.clear()
    assert context.to_dict() == {}


def test_context_to_dict(context: Context) -> None:
    assert context.to_dict() == {'key1': 'str1', 'key2': 'str2', 'key3': 4}


def test_bot_update_init(context: Context, update: Update) -> None:
    bu = BotUpdate('state1', context, update)
    assert bu.state == 'state1'
    assert bu.context == context
    assert bu.message == update.message


def test_bot_update_get_item(bot_update: BotUpdate) -> None:
    assert bot_update['key2'] == 'str2'
    assert bot_update.get('key4') is None


def test_bot_update_set_item(bot_update: BotUpdate) -> None:
    bot_update['key5'] = 6
    assert bot_update['key5'] == 6


def test_bot_update_delitem(bot_update: BotUpdate) -> None:
    assert bot_update['key3'] == 4
    del bot_update['key3']
    assert bot_update.get('key3') is None


def test_bot_update_len(bot_update: BotUpdate) -> None:
    assert len(bot_update) == 3
    bot_update['key6'] = 7
    assert len(bot_update) == 4


def test_bot_update_iter(bot_update: BotUpdate) -> None:
    assert tuple(bot_update) == ('key1', 'key2', 'key3')


def test_bot_update_state(bot_update: BotUpdate) -> None:
    assert bot_update.state == 'state1'


def test_bot_update_state_setter(bot_update: BotUpdate) -> None:
    assert bot_update.state == 'state1'
    bot_update.state = 'state2'
    assert bot_update.state == 'state2'


def test_bot_update_context(bot_update: BotUpdate, context: Context) -> None:
    assert bot_update.context == context


def test_bot_update_update_id(bot_update: BotUpdate) -> None:
    assert bot_update.update_id == 1


def test_bot_update_message(message: Message, bot_update: BotUpdate) -> None:
    assert bot_update.message == message


def test_bot_update_edited_message(message: Message, context: Context) -> None:
    _update = Update(update_id=1, edited_message=message)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.edited_message == message


def test_bot_update_channel_post(message: Message, context: Context) -> None:
    _update = Update(update_id=1, channel_post=message)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.channel_post == message


def test_bot_update_edited_channel_post(message: Message,
                                        context: Context) -> None:
    _update = Update(update_id=1, edited_channel_post=message)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.edited_channel_post == message


def test_bot_update_inline_query(user_dict: _UserDict,
                                 context: Context) -> None:
    inline_query = InlineQuery.from_dict(
        {'id': '1', 'from': user_dict, 'query': 'q', 'offset': 'o'})
    _update = Update(update_id=1, inline_query=inline_query)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.inline_query == inline_query


def test_bot_update_chosen_inline_result(user_dict: _UserDict,
                                         context: Context) -> None:
    chosen_inline_result = ChosenInlineResult.from_dict(
        {'result_id': '1', 'from': user_dict, 'query': 'q'})
    _update = Update(update_id=1, chosen_inline_result=chosen_inline_result)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.chosen_inline_result == chosen_inline_result


def test_bot_update_callback_query(user_dict: _UserDict,
                                   context: Context) -> None:
    callback_query = CallbackQuery.from_dict(
        {'id': '1', 'from': user_dict, 'chat_instance': 'ci'})
    _update = Update(update_id=1, callback_query=callback_query)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.callback_query == callback_query


def test_bot_update_shipping_query(user_dict: _UserDict,
                                   context: Context) -> None:
    shipping_address = {
        'country_code': 'cc', 'state': 's', 'city': 'c', 'street_line1': 'sl1',
        'street_line2': 'sl2', 'post_code': 'pc'}
    shipping_query = ShippingQuery.from_dict(
        {'id': '1', 'from': user_dict, 'invoice_payload': 'ip',
         'shipping_address': shipping_address})
    _update = Update(update_id=1, shipping_query=shipping_query)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.shipping_query == shipping_query


def test_bot_update_pre_checkout_query(user_dict: _UserDict,
                                       context: Context) -> None:
    pre_checkout_query = PreCheckoutQuery.from_dict(
        {'id': '1', 'from': user_dict, 'currency': 'c', 'total_amount': 1,
         'invoice_payload': 'ip'})
    _update = Update(update_id=1, pre_checkout_query=pre_checkout_query)
    _bot_update = BotUpdate('state1', context, _update)
    assert _bot_update.pre_checkout_query == pre_checkout_query
