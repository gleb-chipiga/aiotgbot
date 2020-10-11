from typing import Optional, Union
from unittest.mock import Mock, call

import pytest

from aiotgbot.api_methods import (ApiMethods, ParamsType, _parse_mode_to_str,
                                  _strs_to_json, _to_json)
from aiotgbot.api_types import (APIResponse, Chat, File, KeyboardButton,
                                Message, ReplyKeyboardMarkup, Update, User)
from aiotgbot.constants import ChatAction, ParseMode, RequestMethod
from aiotgbot.utils import json_dumps


@pytest.fixture
def make_msg():
    def _make_message(**params):
        _dict = {
            'message_id': 10,
            'from': {'id': 1, 'is_bot': False, 'first_name': 'fn'},
            'date': 1100,
            'chat': {'id': 1, 'type': 'private'},
            **params
        }
        return Message.from_dict(_dict)

    return _make_message


@pytest.fixture
def reply_kb():
    return ReplyKeyboardMarkup([[
        KeyboardButton('Button')
    ]])


@pytest.fixture
def bot():
    class Bot(ApiMethods):
        request_mock = Mock()
        safe_request_mock = Mock()

        async def _request(self, http_method: RequestMethod, api_method: str,
                           params: Optional[ParamsType] = None) -> APIResponse:
            return self.request_mock(http_method, api_method, params)

        async def _safe_request(
            self, http_method: RequestMethod, api_method: str,
            chat_id: Union[int, str],
            params: Optional[ParamsType] = None
        ) -> APIResponse:
            return self.safe_request_mock(http_method, api_method, chat_id,
                                          params)

    return Bot()


def test_to_json():
    update = Update.from_dict({'update_id': 1})
    assert _to_json(update) == json_dumps(update.to_dict())
    assert _to_json(None) is None


def test_strs_to_json():
    strs = ('str1', 'str2', 'str3')
    assert _strs_to_json(strs) == json_dumps(strs)
    assert _strs_to_json(None) is None


def test_parse_mode_to_str():
    pm = ParseMode.HTML
    assert _parse_mode_to_str(pm) == pm.value
    assert _parse_mode_to_str(None) is None


@pytest.mark.asyncio
async def test_api_methods_get_updates(bot):
    update = Update.from_dict({'update_id': 1})
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': [{'update_id': 1}]})
    assert await bot.get_updates(offset=0, limit=10, timeout=15,
                                 allowed_updates=['message']) == (update,)
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET,
        'getUpdates',
        {'offset': 0, 'limit': 10, 'timeout': 15,
         'allowed_updates': '["message"]'}
    )]


@pytest.mark.asyncio
async def test_api_methods_get_me(bot):
    user = User.from_dict({'id': 1, 'is_bot': False, 'first_name': 'fn'})
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': user.to_dict()})
    assert await bot.get_me() == user
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET, 'getMe', None
    )]


@pytest.mark.asyncio
async def test_api_methods_send_message(bot, make_msg, reply_kb):
    message = make_msg(text='Hello!')
    bot.safe_request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': message.to_dict()})
    assert await bot.send_message(
        chat_id=1,
        text='Hello!',
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=111,
        reply_markup=reply_kb
    ) == message
    assert bot.safe_request_mock.call_args_list == [call(
        RequestMethod.POST,
        'sendMessage',
        1,
        {'text': 'Hello!', 'parse_mode': 'HTML',
         'disable_web_page_preview': True, 'disable_notification': None,
         'reply_to_message_id': 111,
         'reply_markup': json_dumps(reply_kb.to_dict())}
    )]


@pytest.mark.asyncio
async def test_api_methods_send_photo(bot, make_msg, reply_kb):
    message = make_msg(photo=[])
    bot.safe_request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': message.to_dict()})
    assert await bot.send_photo(
        chat_id=1,
        photo='some photo',
        parse_mode=ParseMode.HTML,
        reply_to_message_id=111,
        reply_markup=reply_kb
    ) == message
    assert bot.safe_request_mock.call_args_list == [call(
        RequestMethod.POST,
        'sendPhoto',
        1,
        {'photo': 'some photo', 'caption': None, 'parse_mode': 'HTML',
         'disable_notification': None,
         'reply_to_message_id': 111,
         'reply_markup': json_dumps(reply_kb.to_dict())}
    )]


@pytest.mark.asyncio
async def test_api_methods_forward_message(bot, make_msg):
    message = make_msg(text='Hello!')
    bot.safe_request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': message.to_dict()})
    assert await bot.forward_message(
        chat_id=1,
        from_chat_id=2,
        message_id=9
    ) == message
    assert bot.safe_request_mock.call_args_list == [call(
        RequestMethod.POST,
        'forwardMessage',
        1,
        {'from_chat_id': 2, 'message_id': 9, 'disable_notification': None}
    )]


@pytest.mark.asyncio
async def test_api_methods_send_chat_action(bot):
    bot.safe_request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': True})
    assert await bot.send_chat_action(
        chat_id=1,
        action=ChatAction.TYPING
    )
    assert bot.safe_request_mock.call_args_list == [call(
        RequestMethod.POST,
        'sendChatAction',
        1,
        {'action': ChatAction.TYPING.value}
    )]


@pytest.mark.asyncio
async def test_api_methods_get_file(bot):
    _file = File.from_dict({
        'file_id': '1',
        'file_unique_id': '2',
        'file_size': 11,
        'file_path': 'path'
    })
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': _file.to_dict()})
    assert await bot.get_file(file_id='1')
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET,
        'getFile',
        {'file_id': '1'}
    )]


@pytest.mark.asyncio
async def test_api_methods_leave_chat(bot):
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': True})
    assert await bot.leave_chat(chat_id=1)
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.POST,
        'leaveChat',
        {'chat_id': 1}
    )]


@pytest.mark.asyncio
async def test_api_methods_get_chat(bot):
    chat = Chat.from_dict({
        'id': 1,
        'type': 'private'
    })
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': chat.to_dict()})
    assert await bot.get_chat(chat_id=1)
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET,
        'getChat',
        {'chat_id': 1}
    )]


@pytest.mark.asyncio
async def test_api_methods_answer_callback_query(bot):
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': True})
    assert await bot.answer_callback_query(
        callback_query_id='1',
        text='message',
        show_alert=True
    )
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.POST,
        'answerCallbackQuery',
        {'callback_query_id': '1',
         'text': 'message',
         'show_alert': True,
         'url': None,
         'cache_time': None}
    )]


@pytest.mark.asyncio
async def test_api_methods_edit_message_text(bot, make_msg):
    message = make_msg(text='text2')
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': message.to_dict()})
    assert await bot.edit_message_text(
        text='text2',
        chat_id=1,
        message_id=1
    )
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.POST,
        'editMessageText',
        {'text': 'text2',
         'chat_id': 1,
         'message_id': 1,
         'inline_message_id': None,
         'parse_mode': None,
         'disable_web_page_preview': None,
         'reply_markup': None}
    )]
