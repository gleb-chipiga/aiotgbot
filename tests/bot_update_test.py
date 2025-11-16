import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast

import msgspec
import pytest

from aiotgbot.api_types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Poll,
    PollAnswer,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
)
from aiotgbot.bot_update import BotUpdate, BotUpdateKey, Context, ContextKey
from aiotgbot.helpers import Json


@pytest.fixture
def context() -> Context:
    return Context({"key1": "str1", "key2": "str2", "key3": 4})


@pytest.fixture
def message() -> Message:
    return msgspec.convert(
        {"message_id": 1, "date": 1, "chat": {"id": 1, "type": "private"}},
        Message,
    )


@pytest.fixture
def update(message: Message) -> Update:
    return Update(update_id=1, message=message)


@pytest.fixture
def bot_update(context: Context, update: Update) -> BotUpdate:
    bu = BotUpdate(state="state1", context=context, update=update)
    bu["key1"] = "str1"
    bu["key2"] = "str2"
    bu["key3"] = 4
    return bu


_UserDict = dict[str, int | bool | str]


@dataclass(frozen=True)
class _Payload:
    label: str


@pytest.fixture
def user_dict() -> _UserDict:
    return {"id": 1, "is_bot": False, "first_name": "2"}


def test_context_key() -> None:
    ck1 = ContextKey("key1", int)
    assert ck1.name == "key1"
    assert ck1.type is int
    assert ck1 < ""
    assert repr(ck1) == "<ContextKey(key1, type=int)>"

    ck2 = ContextKey("key2", Update)
    assert ck2.name == "key2"
    assert ck2.type is Update
    assert ck2 < ""
    assert repr(ck2) == "<ContextKey(key2, type=aiotgbot.api_types.Update)>"


def test_context_init() -> None:
    ctx = Context({"1": 2})
    assert ctx.to_dict() == {"1": 2}


def test_context_get_item(context: Context) -> None:
    assert context["key2"] == "str2"
    assert context.get("key4") is None


def test_context_set_item(context: Context) -> None:
    context["key5"] = 6
    assert context.to_dict() == {
        "key1": "str1",
        "key2": "str2",
        "key3": 4,
        "key5": 6,
    }


def test_context_delitem(context: Context) -> None:
    del context["key3"]
    assert context.to_dict() == {"key1": "str1", "key2": "str2"}


def test_context_len(context: Context) -> None:
    assert len(context) == 3
    context["key6"] = 7
    assert len(context) == 4


def test_context_iter(context: Context) -> None:
    assert tuple(context) == ("key1", "key2", "key3")


def test_context_clear(context: Context) -> None:
    assert context.to_dict() == {"key1": "str1", "key2": "str2", "key3": 4}
    context.clear()
    assert context.to_dict() == {}


def test_context_to_dict(context: Context) -> None:
    assert context.to_dict() == {"key1": "str1", "key2": "str2", "key3": 4}


def test_context_set_typed() -> None:
    class A(msgspec.Struct):
        a: int
        b: bool
        c: datetime | None

    k1 = ContextKey("key1", list[A | float])
    k2 = ContextKey("key2", int)
    k3 = ContextKey("key3", str)
    c1 = Context({})
    dt = datetime.now(UTC)
    v: list[A | float] = [
        A(11, False, dt),
        A(22, True, None),
        3.14,
    ]
    c1.set_typed(k1, v)
    c1.set_typed(k2, 10)
    c1.set_typed(k3, "val3")
    j = json.dumps(c1.to_dict())
    c2_data = cast(dict[str, Json], json.loads(j))
    c2 = Context(c2_data)
    assert c2.get_typed(k1) == v
    assert c2.get_typed(k2) == 10
    assert c2.get_typed(k3) == "val3"
    c2.del_typed(k3)
    with pytest.raises(KeyError, match="key3"):
        _ = c2.get_typed(k3)


def test_bot_update_init(context: Context, update: Update) -> None:
    bu = BotUpdate("state1", context, update)
    assert bu.state == "state1"
    assert bu.context == context
    assert bu.message == update.message


def test_bot_update_get_item(bot_update: BotUpdate) -> None:
    assert bot_update["key2"] == "str2"
    assert bot_update.get("key4") is None


def test_bot_update_set_item(bot_update: BotUpdate) -> None:
    bot_update["key5"] = 6
    assert bot_update["key5"] == 6


def test_bot_update_delitem(bot_update: BotUpdate) -> None:
    assert bot_update["key3"] == 4
    del bot_update["key3"]
    assert bot_update.get("key3") is None


def test_bot_update_len(bot_update: BotUpdate) -> None:
    assert len(bot_update) == 3
    bot_update["key6"] = 7
    assert len(bot_update) == 4


def test_bot_update_iter(bot_update: BotUpdate) -> None:
    assert tuple(bot_update) == ("key1", "key2", "key3")


def test_bot_update_state(bot_update: BotUpdate) -> None:
    assert bot_update.state == "state1"


def test_bot_update_state_setter(bot_update: BotUpdate) -> None:
    assert bot_update.state == "state1"
    bot_update.state = "state2"
    assert bot_update.state == "state2"


def test_bot_update_context(bot_update: BotUpdate, context: Context) -> None:
    assert bot_update.context == context


def test_bot_update_update_id(bot_update: BotUpdate) -> None:
    assert bot_update.update_id == 1


def test_bot_update_message(message: Message, bot_update: BotUpdate) -> None:
    assert bot_update.message == message


def test_bot_update_edited_message(message: Message, context: Context) -> None:
    update_obj = Update(update_id=1, edited_message=message)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.edited_message == message


def test_bot_update_channel_post(message: Message, context: Context) -> None:
    update_obj = Update(update_id=1, channel_post=message)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.channel_post == message


def test_bot_update_edited_channel_post(message: Message, context: Context) -> None:
    update_obj = Update(update_id=1, edited_channel_post=message)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.edited_channel_post == message


def test_bot_update_inline_query(user_dict: _UserDict, context: Context) -> None:
    inline_query = msgspec.convert(
        {"id": "1", "from": user_dict, "query": "q", "offset": "o"},
        InlineQuery,
    )
    update_obj = Update(update_id=1, inline_query=inline_query)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.inline_query == inline_query


def test_bot_update_chosen_inline_result(
    user_dict: _UserDict, context: Context
) -> None:
    chosen_inline_result = msgspec.convert(
        {"result_id": "1", "from": user_dict, "query": "q"}, ChosenInlineResult
    )
    update_obj = Update(update_id=1, chosen_inline_result=chosen_inline_result)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.chosen_inline_result == chosen_inline_result


def test_bot_update_callback_query(user_dict: _UserDict, context: Context) -> None:
    callback_query = msgspec.convert(
        {"id": "1", "from": user_dict, "chat_instance": "ci"}, CallbackQuery
    )
    update_obj = Update(update_id=1, callback_query=callback_query)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.callback_query == callback_query


def test_bot_update_shipping_query(user_dict: _UserDict, context: Context) -> None:
    shipping_address = {
        "country_code": "cc",
        "state": "s",
        "city": "c",
        "street_line1": "sl1",
        "street_line2": "sl2",
        "post_code": "pc",
    }
    shipping_query = msgspec.convert(
        {
            "id": "1",
            "from": user_dict,
            "invoice_payload": "ip",
            "shipping_address": shipping_address,
        },
        ShippingQuery,
    )
    update_obj = Update(update_id=1, shipping_query=shipping_query)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.shipping_query == shipping_query


def test_bot_update_pre_checkout_query(user_dict: _UserDict, context: Context) -> None:
    pre_checkout_query = msgspec.convert(
        {
            "id": "1",
            "from": user_dict,
            "currency": "c",
            "total_amount": 1,
            "invoice_payload": "ip",
        },
        PreCheckoutQuery,
    )
    update_obj = Update(update_id=1, pre_checkout_query=pre_checkout_query)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.pre_checkout_query == pre_checkout_query


def test_bot_update_poll(context: Context) -> None:
    poll = msgspec.convert(
        {
            "id": "id",
            "question": "question",
            "options": [],
            "total_voter_count": 3,
            "is_closed": True,
            "is_anonymous": True,
            "type": "quiz",
            "allows_multiple_answers": False,
            "explanation_entities": [],
        },
        Poll,
    )
    update_obj = Update(update_id=1, poll=poll)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.poll == poll


def test_bot_update_poll_answer(context: Context) -> None:
    poll_answer = msgspec.convert(
        {
            "poll_id": "id",
            "user": {"id": 1, "is_bot": False, "first_name": "name"},
            "option_ids": [],
        },
        PollAnswer,
    )
    update_obj = Update(update_id=1, poll_answer=poll_answer)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.poll_answer == poll_answer


def test_bot_update_my_chat_member(context: Context) -> None:
    my_chat_member = msgspec.convert(
        {
            "chat": {"id": 111, "type": "group"},
            "from": {"id": 1, "is_bot": False, "first_name": "name"},
            "date": 123,
            "old_chat_member": {
                "user": {"id": 1, "is_bot": False, "first_name": "name1"},
                "status": "member",
            },
            "new_chat_member": {
                "user": {"id": 1, "is_bot": False, "first_name": "name2"},
                "status": "member",
            },
        },
        ChatMemberUpdated,
    )
    update_obj = Update(update_id=1, my_chat_member=my_chat_member)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.my_chat_member == my_chat_member


def test_bot_update_chat_member(context: Context) -> None:
    chat_member = msgspec.convert(
        {
            "chat": {"id": 111, "type": "group"},
            "from": {"id": 1, "is_bot": False, "first_name": "name"},
            "date": 123,
            "old_chat_member": {
                "user": {"id": 1, "is_bot": False, "first_name": "name1"},
                "status": "member",
            },
            "new_chat_member": {
                "user": {"id": 1, "is_bot": False, "first_name": "name2"},
                "status": "member",
            },
        },
        ChatMemberUpdated,
    )
    update_obj = Update(update_id=1, chat_member=chat_member)
    bot_update = BotUpdate("state1", context, update_obj)
    assert bot_update.chat_member == chat_member


def test_bot_update_allows_arbitrary_payload(context: Context, update: Update) -> None:
    payload = _Payload("any")
    bot_update = BotUpdate(state="state1", context=context, update=update)
    bot_update["payload"] = payload
    bot_update["another"] = 12
    assert bot_update["payload"] is payload
    assert bot_update["another"] == 12


def test_bot_update_key_roundtrip(context: Context, update: Update) -> None:
    key = BotUpdateKey("session", _Payload)
    bot_update = BotUpdate(state="state1", context=context, update=update)
    payload = _Payload("typed")
    bot_update.set_typed(key, payload)
    result = bot_update.get_typed(key)
    assert result is payload
    bot_update.del_typed(key)
    with pytest.raises(KeyError):
        _ = bot_update.get_typed(key)


def test_bot_update_key_set_type_guard(context: Context, update: Update) -> None:
    key = BotUpdateKey("session", _Payload)
    bot_update = BotUpdate(state="state1", context=context, update=update)
    with pytest.raises(TypeError, match="expected type _Payload"):
        bot_update.set_typed(key, cast(_Payload, cast(object, "wrong")))


def test_bot_update_key_get_type_guard(context: Context, update: Update) -> None:
    key = BotUpdateKey("session", _Payload)
    bot_update = BotUpdate(state="state1", context=context, update=update)
    bot_update["session"] = "wrong"
    with pytest.raises(TypeError, match="expected value of type _Payload"):
        _ = bot_update.get_typed(key)
