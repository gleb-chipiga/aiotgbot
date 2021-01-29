from io import BytesIO
from typing import Any, AsyncIterator, Callable, Union, cast
from unittest.mock import Mock, call

import pytest

from aiotgbot import api_methods
from aiotgbot.api_methods import ApiMethods, ParamType
from aiotgbot.api_types import (APIResponse, Chat, File, InputMediaPhoto,
                                KeyboardButton, Message, ReplyKeyboardMarkup,
                                StreamFile, Update, User)
from aiotgbot.constants import ChatAction, ParseMode, RequestMethod, UpdateType
from aiotgbot.helpers import json_dumps

_MakeMessage = Callable[..., Message]


@pytest.fixture
def make_message() -> _MakeMessage:
    def _make_message(**kwargs: Any) -> Message:
        _dict = {
            'message_id': 10,
            'from': {'id': 1, 'is_bot': False, 'first_name': 'fn'},
            'date': 1100,
            'chat': {'id': 1, 'type': 'private'},
            **kwargs
        }
        return Message.from_dict(_dict)
    return _make_message


@pytest.fixture
def reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[
        KeyboardButton('Button')
    ]])


async def _iter_bytes(
    data: bytes, chunk_size: int = 2 ** 16
) -> AsyncIterator[bytes]:
    bytes_io = BytesIO(data)
    while len(chunk := bytes_io.read(chunk_size)) > 0:
        yield chunk


def stream_file(string: str) -> StreamFile:
    return StreamFile(content=_iter_bytes(string.encode()), name=string)


class Bot(ApiMethods):

    def __init__(self) -> None:
        self.request_mock = Mock()
        self.safe_request_mock = Mock()

    async def _request(self, http_method: RequestMethod, api_method: str,
                       **params: ParamType) -> APIResponse:
        return cast(APIResponse, self.request_mock(http_method, api_method,
                                                   **params))

    async def _safe_request(
        self, http_method: RequestMethod, api_method: str,
        chat_id: Union[int, str], **params: ParamType
    ) -> APIResponse:
        return cast(APIResponse, self.safe_request_mock(
            http_method, api_method, chat_id, **params))


@pytest.fixture
def bot() -> Bot:
    return Bot()


def test_to_json() -> None:
    update = Update.from_dict({'update_id': 1})
    assert api_methods._to_json(update) == json_dumps(update.to_dict())
    assert api_methods._to_json(None) is None


def test_strs_to_json() -> None:
    strs = ('str1', 'str2', 'str3')
    assert api_methods._strs_to_json(strs) == json_dumps(strs)
    assert api_methods._strs_to_json(None) is None


def test_parse_mode_to_str() -> None:
    pm = ParseMode.HTML
    assert api_methods._parse_mode_to_str(pm) == pm.value
    assert api_methods._parse_mode_to_str(None) is None


@pytest.mark.asyncio
async def test_api_methods_get_updates(bot: Bot) -> None:
    update = Update.from_dict({'update_id': 1})
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': [{'update_id': 1}]})
    assert await bot.get_updates(
        offset=0, limit=10, timeout=15,
        allowed_updates=[UpdateType.MESSAGE]) == (update,)
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET,
        'getUpdates',
        offset=0,
        limit=10,
        timeout=15,
        allowed_updates='["message"]'
    )]


@pytest.mark.asyncio
async def test_api_methods_get_me(bot: Bot) -> None:
    user = User.from_dict({'id': 1, 'is_bot': False, 'first_name': 'fn'})
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': user.to_dict()})
    assert await bot.get_me() == user
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET, 'getMe'
    )]


@pytest.mark.asyncio
async def test_api_methods_send_message(bot: Bot, make_message: _MakeMessage,
                                        reply_kb: ReplyKeyboardMarkup) -> None:
    message = make_message(text='Hello!')
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
        text='Hello!',
        parse_mode='HTML',
        entities=None,
        disable_web_page_preview=True,
        disable_notification=None,
        reply_to_message_id=111,
        allow_sending_without_reply=None,
        reply_markup=json_dumps(reply_kb.to_dict())
    )]


@pytest.mark.asyncio
async def test_api_methods_send_photo(bot: Bot, make_message: _MakeMessage,
                                      reply_kb: ReplyKeyboardMarkup) -> None:
    message = make_message(photo=[])
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
        'sendPhoto', 1,
        photo='some photo',
        caption=None,
        parse_mode='HTML',
        caption_entities=None,
        disable_notification=None,
        reply_to_message_id=111,
        allow_sending_without_reply=None,
        reply_markup=json_dumps(reply_kb.to_dict())
    )]


@pytest.mark.asyncio
async def test_api_methods_forward_message(bot: Bot,
                                           make_message: _MakeMessage) -> None:
    message = make_message(text='Hello!')
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
        from_chat_id=2,
        message_id=9,
        disable_notification=None
    )]


@pytest.mark.asyncio
async def test_api_methods_send_chat_action(bot: Bot) -> None:
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
        action=ChatAction.TYPING.value
    )]


@pytest.mark.asyncio
async def test_api_methods_get_file(bot: Bot) -> None:
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
        file_id='1'
    )]


@pytest.mark.asyncio
async def test_api_methods_leave_chat(bot: Bot) -> None:
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': True})
    assert await bot.leave_chat(chat_id=1)
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.POST,
        'leaveChat',
        chat_id=1
    )]


@pytest.mark.asyncio
async def test_api_methods_get_chat(bot: Bot) -> None:
    chat = Chat.from_dict({
        'id': 1,
        'type': 'private'
    })
    bot.request_mock.return_value = APIResponse.from_dict(
        {'ok': True, 'result': chat.to_dict()})
    assert await bot.get_chat(chat_id=1)
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.GET, 'getChat', chat_id=1
    )]


@pytest.mark.asyncio
async def test_api_methods_answer_callback_query(bot: Bot) -> None:
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
        callback_query_id='1',
        text='message',
        show_alert=True,
        url=None,
        cache_time=None
    )]


@pytest.mark.asyncio
async def test_api_methods_edit_message_text(
    bot: Bot, make_message: _MakeMessage
) -> None:
    message = make_message(text='text2')
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
        text='text2',
        chat_id=1,
        message_id=1,
        inline_message_id=None,
        parse_mode=None,
        entities=None,
        disable_web_page_preview=None,
        reply_markup=None
    )]


@pytest.mark.asyncio
async def test_send_media_group(bot: Bot, make_message: _MakeMessage) -> None:
    file0 = stream_file('bytes1')
    file1 = stream_file('bytes2')
    file2 = stream_file('bytes3')

    bot.safe_request_mock.return_value = APIResponse.from_dict({
        'ok': True,
        'result': [make_message().to_dict(), make_message().to_dict(),
                   make_message().to_dict()]
    })

    await bot.send_media_group(
        1,
        media=(
            InputMediaPhoto(media=file0, caption='f1'),
            InputMediaPhoto(media=file1, caption='f2'),
            InputMediaPhoto(media=file2, caption='f3')
        )
    )

    assert bot.safe_request_mock.call_args_list == [call(
        RequestMethod.POST,
        'sendMediaGroup',
        1,
        media=json_dumps([
            InputMediaPhoto(media='attach://attachment0',
                            caption='f1').to_dict(),
            InputMediaPhoto(media='attach://attachment1',
                            caption='f2').to_dict(),
            InputMediaPhoto(media='attach://attachment2',
                            caption='f3').to_dict()
        ]),
        disable_notification=None,
        reply_to_message_id=None,
        allow_sending_without_reply=None,
        attachment0=file0,
        attachment1=file1,
        attachment2=file2
    )]


@pytest.mark.asyncio
async def test_edit_message_media(
    bot: Bot, make_message: _MakeMessage
) -> None:
    file = stream_file('bytes1')
    bot.request_mock.return_value = APIResponse.from_dict({
        'ok': True,
        'result': make_message().to_dict()
    })
    await bot.edit_message_media(
        media=InputMediaPhoto(media=file, caption='f1'),
        chat_id=1,
        message_id=1
    )
    assert bot.request_mock.call_args_list == [call(
        RequestMethod.POST,
        'editMessageMedia',
        chat_id=1,
        message_id=1,
        inline_message_id=None,
        media=json_dumps(InputMediaPhoto(media='attach://attachment0',
                         caption='f1').to_dict()),
        reply_markup=None,
        attachment0=file
    )]
