import pytest

from aiotgbot.api_types import Message, Update
from aiotgbot.bot import Bot, Handler
from aiotgbot.bot_update import BotUpdate, Context
from aiotgbot.filters import StateFilter, UpdateType, UpdateTypeFilter
from aiotgbot.handler_table import HandlerTable
from aiotgbot.storage_memory import MemoryStorage


@pytest.fixture
def bot():
    bot = Bot('token', HandlerTable(), MemoryStorage())
    bot['key1'] = 'str1'
    bot['key2'] = 'str2'
    bot['key3'] = 4

    return bot


def test_bot_get_item(bot):
    assert bot['key2'] == 'str2'
    assert bot.get('key4') is None


def test_bot_set_item(bot):
    bot['key5'] = 6
    assert bot['key5'] == 6


def test_bot_delitem(bot):
    assert bot['key3'] == 4
    del bot['key3']
    assert bot.get('key3') is None


def test_bot_len(bot):
    assert len(bot) == 3
    bot['key6'] = 7
    assert len(bot) == 4


def test_bot_iter(bot):
    assert tuple(bot) == ('key1', 'key2', 'key3')


def test_bot_storage(bot):
    assert isinstance(bot.storage, MemoryStorage)


@pytest.mark.asyncio
async def test_handler_check():
    async def func1(bot, update): ...

    handler = Handler(func1, (
        UpdateTypeFilter(UpdateType.MESSAGE),
        StateFilter('state1'),
    ))

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
    assert await handler.check(_bot, bu1)
    bu2 = BotUpdate('state2', ctx, Update(update_id=2, **params))
    assert not await handler.check(_bot, bu2)
