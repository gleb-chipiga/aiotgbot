import asyncio
from collections.abc import AsyncIterator, Callable
from io import BytesIO
from typing import TypeVar, cast
from unittest.mock import Mock, call

import msgspec
import pytest
from typing_extensions import override  # Python 3.11 compatibility

from aiotgbot.api_methods import ApiMethods, ParamType
from aiotgbot.api_types import (
    Attach,
    BotCommand,
    BotCommandScopeChat,
    CallbackQueryId,
    Chat,
    ChatId,
    File,
    FileId,
    InputMediaPhoto,
    KeyboardButton,
    Message,
    MessageId,
    ReplyKeyboardMarkup,
    StreamFile,
    Update,
    User,
)
from aiotgbot.constants import ChatAction, ParseMode, RequestMethod, UpdateType

_MakeMessage = Callable[..., Message]


@pytest.fixture
def make_message() -> _MakeMessage:
    def _make_message(**kwargs: object) -> Message:
        message_dict = {
            "message_id": 10,
            "from": {"id": 1, "is_bot": False, "first_name": "fn"},
            "date": 1100,
            "chat": {"id": 1, "type": "private"},
            **kwargs,
        }
        return msgspec.convert(message_dict, Message)

    return _make_message


@pytest.fixture
def reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Button")]])


async def _iter_bytes(data: bytes, chunk_size: int = 2**16) -> AsyncIterator[bytes]:
    bytes_io = BytesIO(data)
    while len(chunk := bytes_io.read(chunk_size)) > 0:
        await asyncio.sleep(0)
        yield chunk


def stream_file(string: str) -> StreamFile:
    return StreamFile(content=_iter_bytes(string.encode()), name=string)


T = TypeVar("T")


class Bot(ApiMethods):
    def __init__(self) -> None:
        self.request_mock: Mock = Mock()
        self.safe_request_mock: Mock = Mock()

    @override
    async def _request(
        self,
        http_method: RequestMethod,
        api_method: str,
        type_: type[T],
        **params: ParamType,
    ) -> T:
        return cast(T, self.request_mock(http_method, api_method, **params))

    @override
    async def _safe_request(
        self,
        http_method: RequestMethod,
        api_method: str,
        chat_id: int | str,
        type_: type[T],
        **params: ParamType,
    ) -> T:
        return cast(
            T,
            self.safe_request_mock(http_method, api_method, chat_id, **params),
        )


@pytest.fixture
def bot() -> Bot:
    return Bot()


@pytest.mark.asyncio
async def test_api_methods_get_updates(bot: Bot) -> None:
    update = msgspec.convert({"update_id": 1}, Update)
    bot.request_mock.return_value = msgspec.convert(
        [{"update_id": 1}], tuple[Update, ...]
    )
    assert await bot.get_updates(
        offset=0, limit=10, timeout=15, allowed_updates=[UpdateType.MESSAGE]
    ) == (update,)
    assert bot.request_mock.call_args_list == [
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
async def test_api_methods_get_me(bot: Bot) -> None:
    user = msgspec.convert({"id": 1, "is_bot": False, "first_name": "fn"}, User)
    bot.request_mock.return_value = user
    assert await bot.get_me() == user
    assert bot.request_mock.call_args_list == [call(RequestMethod.GET, "getMe")]


@pytest.mark.asyncio
async def test_api_methods_send_message(
    bot: Bot, make_message: _MakeMessage, reply_kb: ReplyKeyboardMarkup
) -> None:
    message = make_message(text="Hello!")
    bot.safe_request_mock.return_value = message

    assert (
        await bot.send_message(
            chat_id=ChatId(1),
            text="Hello!",
            message_thread_id=None,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_kb,
        )
        == message
    )
    assert bot.safe_request_mock.call_args_list == [
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
    bot: Bot, make_message: _MakeMessage, reply_kb: ReplyKeyboardMarkup
) -> None:
    message = make_message(photo=[])
    bot.safe_request_mock.return_value = message
    assert (
        await bot.send_photo(
            chat_id=ChatId(1),
            photo=FileId("some photo"),
            message_thread_id=None,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_kb,
        )
        == message
    )
    assert bot.safe_request_mock.call_args_list == [
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
    bot: Bot, make_message: _MakeMessage
) -> None:
    message = make_message(text="Hello!")
    bot.safe_request_mock.return_value = message
    assert (
        await bot.forward_message(
            chat_id=ChatId(1),
            from_chat_id=ChatId(2),
            message_id=MessageId(9),
        )
        == message
    )
    assert bot.safe_request_mock.call_args_list == [
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
async def test_api_methods_send_chat_action(bot: Bot) -> None:
    bot.safe_request_mock.return_value = True
    assert await bot.send_chat_action(chat_id=ChatId(1), action=ChatAction.TYPING)
    assert bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "sendChatAction",
            1,
            action=ChatAction.TYPING,
            message_thread_id=None,
        )
    ]


@pytest.mark.asyncio
async def test_api_methods_get_file(bot: Bot) -> None:
    file_response = msgspec.convert(
        {
            "file_id": "1",
            "file_unique_id": "2",
            "file_size": 11,
            "file_path": "path",
        },
        File,
    )
    bot.request_mock.return_value = file_response
    assert await bot.get_file(file_id=FileId("1"))
    assert bot.request_mock.call_args_list == [
        call(RequestMethod.GET, "getFile", file_id="1")
    ]


@pytest.mark.asyncio
async def test_api_methods_leave_chat(bot: Bot) -> None:
    bot.request_mock.return_value = True
    assert await bot.leave_chat(chat_id=ChatId(1))
    assert bot.request_mock.call_args_list == [
        call(RequestMethod.POST, "leaveChat", chat_id=1)
    ]


@pytest.mark.asyncio
async def test_api_methods_get_chat(bot: Bot) -> None:
    chat = msgspec.convert({"id": 1, "type": "private"}, Chat)
    bot.request_mock.return_value = chat
    assert await bot.get_chat(chat_id=ChatId(1))
    assert bot.request_mock.call_args_list == [
        call(RequestMethod.GET, "getChat", chat_id=1)
    ]


@pytest.mark.asyncio
async def test_api_methods_answer_callback_query(bot: Bot) -> None:
    bot.request_mock.return_value = True
    assert await bot.answer_callback_query(
        callback_query_id=CallbackQueryId("1"), text="message", show_alert=True
    )
    assert bot.request_mock.call_args_list == [
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
    bot: Bot, make_message: _MakeMessage
) -> None:
    message = make_message(text="text2")
    bot.request_mock.return_value = message
    assert await bot.edit_message_text(
        text="text2", chat_id=ChatId(1), message_id=MessageId(1)
    )
    assert bot.request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "editMessageText",
            text="text2",
            chat_id=1,
            message_id=1,
            parse_mode=None,
            entities=None,
            link_preview_options=None,
            reply_markup=None,
        )
    ]


@pytest.mark.asyncio
async def test_send_media_group(bot: Bot, make_message: _MakeMessage) -> None:
    file0 = stream_file("bytes1")
    file1 = stream_file("bytes2")
    file2 = stream_file("bytes3")

    bot.safe_request_mock.return_value = (
        make_message(),
        make_message(),
        make_message(),
    )

    _ = await bot.send_media_group(
        ChatId(1),
        media=(
            InputMediaPhoto(media=file0, caption="f1"),
            InputMediaPhoto(media=file1, caption="f2"),
            InputMediaPhoto(media=file2, caption="f3"),
        ),
    )

    assert bot.safe_request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "sendMediaGroup",
            1,
            media=msgspec.json.encode([
                InputMediaPhoto(media=Attach("attach://attachment0"), caption="f1"),
                InputMediaPhoto(media=Attach("attach://attachment1"), caption="f2"),
                InputMediaPhoto(media=Attach("attach://attachment2"), caption="f3"),
            ]).decode(),
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
async def test_edit_message_media(bot: Bot, make_message: _MakeMessage) -> None:
    file = stream_file("bytes1")
    bot.request_mock.return_value = make_message()
    _ = await bot.edit_message_media(
        media=InputMediaPhoto(media=file, caption="f1"),
        chat_id=ChatId(1),
        message_id=MessageId(1),
    )
    assert bot.request_mock.call_args_list == [
        call(
            RequestMethod.POST,
            "editMessageMedia",
            chat_id=1,
            message_id=1,
            media=msgspec.json.encode(
                InputMediaPhoto(
                    media=Attach("attach://attachment0"),
                    caption="f1",
                )
            ).decode(),
            reply_markup=None,
            attachment0=file,
        )
    ]


@pytest.mark.asyncio
async def test_get_my_commands(bot: Bot) -> None:
    commands = (
        BotCommand(command="cmd1", description="Command 1"),
        BotCommand(command="cmd2", description="Command 2"),
    )
    bot.request_mock.return_value = commands
    assert (
        await bot.get_my_commands(BotCommandScopeChat(chat_id=ChatId(123)), "ru")
        == commands
    )
    assert bot.request_mock.call_args_list == [
        call(
            RequestMethod.GET,
            "getMyCommands",
            scope='{"type":"chat","chat_id":123}',
            language_code="ru",
        )
    ]
