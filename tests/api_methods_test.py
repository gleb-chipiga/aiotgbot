from io import BytesIO
from typing import Any, AsyncIterator, Callable, Type, TypeVar, cast
from unittest.mock import Mock, call

import msgspec
import pytest
import pytest_asyncio

from aiotgbot.api_methods import ApiMethods, ParamType
from aiotgbot.api_types import (
    BotCommand,
    BotCommandScopeChat,
    Chat,
    File,
    InputMediaPhoto,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    StreamFile,
    Update,
    User,
)
from aiotgbot.constants import ChatAction, ParseMode, RequestMethod, UpdateType

_MakeMessage = Callable[..., Message]


@pytest.fixture
def make_message() -> _MakeMessage:
    def _make_message(**kwargs: Any) -> Message:
        _dict = {
            "message_id": 10,
            "from": {"id": 1, "is_bot": False, "first_name": "fn"},
            "date": 1100,
            "chat": {"id": 1, "type": "private"},
            **kwargs,
        }
        return msgspec.convert(_dict, Message)

    return _make_message


@pytest.fixture
def reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton("Button")]])


async def _iter_bytes(
    data: bytes, chunk_size: int = 2**16
) -> AsyncIterator[bytes]:
    bytes_io = BytesIO(data)
    while len(chunk := bytes_io.read(chunk_size)) > 0:
        yield chunk


def stream_file(string: str) -> StreamFile:
    return StreamFile(content=_iter_bytes(string.encode()), name=string)


T = TypeVar("T")


class Bot(ApiMethods):
    def __init__(self) -> None:
        self.request_mock = Mock()
        self.safe_request_mock = Mock()

    async def _request(
        self,
        http_method: RequestMethod,
        api_method: str,
        type_: Type[T],
        **params: ParamType,
    ) -> T:
        return cast(T, self.request_mock(http_method, api_method, **params))

    async def _safe_request(
        self,
        http_method: RequestMethod,
        api_method: str,
        chat_id: int | str,
        type_: Type[T],
        **params: ParamType,
    ) -> T:
        return cast(
            T,
            self.safe_request_mock(http_method, api_method, chat_id, **params),
        )


@pytest_asyncio.fixture
async def _bot() -> Bot:
    return Bot()


@pytest.mark.asyncio
async def test_api_methods_get_updates(_bot: Bot) -> None:
    update = msgspec.convert({"update_id": 1}, Update)
    _bot.request_mock.return_value = msgspec.convert(
        [{"update_id": 1}], tuple[Update, ...]
    )
    assert await _bot.get_updates(
        offset=0, limit=10, timeout=15, allowed_updates=[UpdateType.MESSAGE]
    ) == (update,)
    assert _bot.request_mock.call_args_list == [
        call(
            RequestMethod.GET,
            "getUpdates",
            offset=0,
            limit=10,
            timeout=15,
            allowed_updates='["message"]',
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_get_me(_bot: Bot) -> None:
    user = msgspec.convert(
        {"id": 1, "is_bot": False, "first_name": "fn"}, User
    )
    _bot.request_mock.return_value = user
    assert await _bot.get_me() == user
    assert _bot.request_mock.call_args_list == [
        call(RequestMethod.GET, "getMe")
    ]


@pytest.mark.asyncio
async def test_api_methods_send_message(
    _bot: Bot, make_message: _MakeMessage, reply_kb: ReplyKeyboardMarkup
) -> None:
    message = make_message(text="Hello!")
    _bot.safe_request_mock.return_value = message

    assert (
        await _bot.send_message(
            chat_id=1,
            text="Hello!",
            message_thread_id=None,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_kb,
        )
        == message
    )
    assert _bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "sendMessage",
            1,
            text="Hello!",
            message_thread_id=None,
            parse_mode="HTML",
            entities=None,
            link_preview_options=None,
            disable_notification=None,
            protect_content=None,
            reply_parameters=None,
            reply_markup=msgspec.json.encode(reply_kb).decode(),
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_send_photo(
    _bot: Bot, make_message: _MakeMessage, reply_kb: ReplyKeyboardMarkup
) -> None:
    message = make_message(photo=[])
    _bot.safe_request_mock.return_value = message
    assert (
        await _bot.send_photo(
            chat_id=1,
            photo="some photo",
            message_thread_id=None,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_kb,
        )
        == message
    )
    assert _bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "sendPhoto",
            1,
            photo="some photo",
            message_thread_id=None,
            caption=None,
            parse_mode="HTML",
            caption_entities=None,
            has_spoiler=None,
            disable_notification=None,
            protect_content=None,
            reply_parameters=None,
            reply_markup=msgspec.json.encode(reply_kb).decode(),
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_forward_message(
    _bot: Bot, make_message: _MakeMessage
) -> None:
    message = make_message(text="Hello!")
    _bot.safe_request_mock.return_value = message
    assert (
        await _bot.forward_message(chat_id=1, from_chat_id=2, message_id=9)
        == message
    )
    assert _bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "forwardMessage",
            1,
            from_chat_id=2,
            message_id=9,
            message_thread_id=None,
            disable_notification=None,
            protect_content=None,
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_send_chat_action(_bot: Bot) -> None:
    _bot.safe_request_mock.return_value = True
    assert await _bot.send_chat_action(chat_id=1, action=ChatAction.TYPING)
    assert _bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "sendChatAction",
            1,
            action=ChatAction.TYPING,
            message_thread_id=None,
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_get_file(_bot: Bot) -> None:
    _file = msgspec.convert(
        {
            "file_id": "1",
            "file_unique_id": "2",
            "file_size": 11,
            "file_path": "path",
        },
        File,
    )
    _bot.request_mock.return_value = _file
    assert await _bot.get_file(file_id="1")
    assert _bot.request_mock.call_args_list == [
        call(RequestMethod.GET, "getFile", file_id="1")
    ]


@pytest.mark.asyncio
async def test_api_methods_leave_chat(_bot: Bot) -> None:
    _bot.request_mock.return_value = True
    assert await _bot.leave_chat(chat_id=1)
    assert _bot.request_mock.call_args_list == [
        call(RequestMethod.POST, "leaveChat", chat_id=1)
    ]


@pytest.mark.asyncio
async def test_api_methods_get_chat(_bot: Bot) -> None:
    chat = msgspec.convert({"id": 1, "type": "private"}, Chat)
    _bot.request_mock.return_value = chat
    assert await _bot.get_chat(chat_id=1)
    assert _bot.request_mock.call_args_list == [
        call(RequestMethod.GET, "getChat", chat_id=1)
    ]


@pytest.mark.asyncio
async def test_api_methods_answer_callback_query(_bot: Bot) -> None:
    _bot.request_mock.return_value = True
    assert await _bot.answer_callback_query(
        callback_query_id="1", text="message", show_alert=True
    )
    assert _bot.request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "answerCallbackQuery",
            callback_query_id="1",
            text="message",
            show_alert=True,
            url=None,
            cache_time=None,
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_edit_message_text(
    _bot: Bot, make_message: _MakeMessage
) -> None:
    message = make_message(text="text2")
    _bot.request_mock.return_value = message
    assert await _bot.edit_message_text(text="text2", chat_id=1, message_id=1)
    assert _bot.request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "editMessageText",
            text="text2",
            chat_id=1,
            message_id=1,
            inline_message_id=None,
            parse_mode=None,
            entities=None,
            link_preview_options=None,
            reply_markup=None,
        )
    ]


@pytest.mark.asyncio
async def test_send_media_group(_bot: Bot, make_message: _MakeMessage) -> None:
    file0 = stream_file("bytes1")
    file1 = stream_file("bytes2")
    file2 = stream_file("bytes3")

    _bot.safe_request_mock.return_value = (
        make_message(),
        make_message(),
        make_message(),
    )

    await _bot.send_media_group(
        1,
        media=(
            InputMediaPhoto(media=file0, caption="f1"),
            InputMediaPhoto(media=file1, caption="f2"),
            InputMediaPhoto(media=file2, caption="f3"),
        ),
    )

    assert _bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "sendMediaGroup",
            1,
            media=msgspec.json.encode(
                [
                    InputMediaPhoto(
                        media="attach://attachment0", caption="f1"
                    ),
                    InputMediaPhoto(
                        media="attach://attachment1", caption="f2"
                    ),
                    InputMediaPhoto(
                        media="attach://attachment2", caption="f3"
                    ),
                ]
            ).decode(),
            message_thread_id=None,
            disable_notification=None,
            protect_content=None,
            reply_parameters=None,
            attachment0=file0,
            attachment1=file1,
            attachment2=file2,
        )
    ]


@pytest.mark.asyncio
async def test_edit_message_media(
    _bot: Bot, make_message: _MakeMessage
) -> None:
    file = stream_file("bytes1")
    _bot.request_mock.return_value = make_message()
    await _bot.edit_message_media(
        media=InputMediaPhoto(media=file, caption="f1"),
        chat_id=1,
        message_id=1,
    )
    assert _bot.request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "editMessageMedia",
            chat_id=1,
            message_id=1,
            inline_message_id=None,
            media=msgspec.json.encode(
                InputMediaPhoto(media="attach://attachment0", caption="f1")
            ).decode(),
            reply_markup=None,
            attachment0=file,
        )
    ]


@pytest.mark.asyncio
async def test_get_my_commands(_bot: Bot, make_message: _MakeMessage) -> None:
    commands = (
        BotCommand("cmd1", "Command 1"),
        BotCommand("cmd2", "Command 2"),
    )
    _bot.request_mock.return_value = commands
    assert (
        await _bot.get_my_commands(BotCommandScopeChat(123), "ru") == commands
    )
    assert _bot.request_mock.call_args_list == [
        call(
            RequestMethod.GET,
            "getMyCommands",
            scope='{"type":"chat","chat_id":123}',
            language_code="ru",
        )
    ]
