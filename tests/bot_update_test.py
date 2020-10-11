import pytest

from aiotgbot.api_types import (CallbackQuery, ChosenInlineResult, InlineQuery,
                                Message, PreCheckoutQuery, ShippingQuery,
                                Update)
from aiotgbot.bot_update import BotUpdate, Context


@pytest.fixture
def ctx():
    return Context({'key1': 'str1', 'key2': 'str2', 'key3': 4})


@pytest.fixture
def make_upd():
    def _make_update(update_id=1, **params):
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
        return Update(update_id, **params)

    return _make_update


@pytest.fixture
def make_bu(ctx, make_upd):
    def _make_bu(**params):
        return BotUpdate('state1', ctx, make_upd(**params))

    return _make_bu


@pytest.fixture
def msg():
    return Message.from_dict({'message_id': 1, 'date': 1,
                              'chat': {'id': 1, 'type': 'private'}})


@pytest.fixture
def bu(ctx, msg, make_upd):
    _bu = BotUpdate('state1', ctx, make_upd(message=msg))
    _bu['key1'] = 'str1'
    _bu['key2'] = 'str2'
    _bu['key3'] = 4

    return _bu


@pytest.fixture
def user_dict():
    return {'id': 1, 'is_bot': False, 'first_name': '2'}


def test_context_init():
    ctx = Context({'1': 2})
    assert ctx.to_dict() == {'1': 2}


def test_context_get_item(ctx):
    assert ctx['key2'] == 'str2'
    assert ctx.get('key4') is None


def test_context_set_item(ctx):
    ctx['key5'] = 6
    assert ctx.to_dict() == {'key1': 'str1', 'key2': 'str2', 'key3': 4,
                             'key5': 6}


def test_context_delitem(ctx):
    del ctx['key3']
    assert ctx.to_dict() == {'key1': 'str1', 'key2': 'str2'}


def test_context_len(ctx):
    assert len(ctx) == 3
    ctx['key6'] = 7
    assert len(ctx) == 4


def test_context_iter(ctx):
    assert tuple(ctx) == ('key1', 'key2', 'key3')


def test_context_reset(ctx):
    assert ctx.to_dict() == {'key1': 'str1', 'key2': 'str2', 'key3': 4}
    ctx.reset()
    assert ctx.to_dict() == {}


def test_context_to_dict(ctx):
    assert ctx.to_dict() == {'key1': 'str1', 'key2': 'str2', 'key3': 4}


def test_bot_update_init(ctx, msg, make_upd):
    bu = BotUpdate('state1', ctx, make_upd(message=msg))
    assert bu.state == 'state1'
    assert bu.context == ctx
    assert bu.message == msg


def test_bot_update_get_item(bu):
    assert bu['key2'] == 'str2'
    assert bu.get('key4') is None


def test_bot_update_set_item(bu):
    bu['key5'] = 6
    assert bu['key5'] == 6


def test_bot_update_delitem(bu):
    assert bu['key3'] == 4
    del bu['key3']
    assert bu.get('key3') is None


def test_bot_update_len(bu):
    assert len(bu) == 3
    bu['key6'] = 7
    assert len(bu) == 4


def test_bot_update_iter(bu):
    assert tuple(bu) == ('key1', 'key2', 'key3')


def test_bot_update_state(bu):
    assert bu.state == 'state1'


def test_bot_update_state_setter(bu):
    assert bu.state == 'state1'
    bu.state = 'state2'
    assert bu.state == 'state2'


def test_bot_update_context(bu, ctx):
    assert bu.context == ctx


def test_bot_update_update_id(bu):
    assert bu.update_id == 1


def test_bot_update_message(msg, make_bu):
    bu = make_bu(message=msg)
    assert bu.message == msg


def test_bot_update_edited_message(msg, make_bu):
    bu = make_bu(edited_message=msg)
    assert bu.edited_message == msg


def test_bot_update_channel_post(msg, make_bu):
    bu = make_bu(channel_post=msg)
    assert bu.channel_post == msg


def test_bot_update_edited_channel_post(msg, make_bu):
    bu = make_bu(edited_channel_post=msg)
    assert bu.edited_channel_post == msg


def test_bot_update_inline_query(make_bu, user_dict):
    inline_query = InlineQuery.from_dict(
        {'id': '1', 'from': user_dict, 'query': 'q', 'offset': 'o'})
    bu = make_bu(inline_query=inline_query)
    assert bu.inline_query == inline_query


def test_bot_update_chosen_inline_result(make_bu, user_dict):
    chosen_inline_result = ChosenInlineResult.from_dict(
        {'result_id': '1', 'from': user_dict, 'query': 'q'})
    bu = make_bu(chosen_inline_result=chosen_inline_result)
    assert bu.chosen_inline_result == chosen_inline_result


def test_bot_update_callback_query(make_bu, user_dict):
    callback_query = CallbackQuery.from_dict(
        {'id': '1', 'from': user_dict, 'chat_instance': 'ci'})
    bu = make_bu(callback_query=callback_query)
    assert bu.callback_query == callback_query


def test_bot_update_shipping_query(make_bu, user_dict):
    shipping_address = {
        'country_code': 'cc', 'state': 's', 'city': 'c', 'street_line1': 'sl1',
        'street_line2': 'sl2', 'post_code': 'pc'}
    shipping_query = ShippingQuery.from_dict(
        {'id': '1', 'from': user_dict, 'invoice_payload': 'ip',
         'shipping_address': shipping_address})
    bu = make_bu(shipping_query=shipping_query)
    assert bu.shipping_query == shipping_query


def test_bot_update_pre_checkout_query(make_bu, user_dict):
    pre_checkout_query = PreCheckoutQuery.from_dict(
        {'id': '1', 'from': user_dict, 'currency': 'c', 'total_amount': 1,
         'invoice_payload': 'ip'})
    bu = make_bu(pre_checkout_query=pre_checkout_query)
    assert bu.pre_checkout_query == pre_checkout_query
