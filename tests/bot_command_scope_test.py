import msgspec
import pytest

from aiotgbot.api_types import (
    BotCommandScope,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
    BotCommandScopeDefault,
)


@pytest.mark.parametrize(
    "scope,json",
    (
        (
            BotCommandScopeDefault(),
            b'{"type":"default"}',
        ),
        (
            BotCommandScopeAllPrivateChats(),
            b'{"type":"all_private_chats"}',
        ),
        (
            BotCommandScopeAllGroupChats(),
            b'{"type":"all_group_chats"}',
        ),
        (
            BotCommandScopeAllChatAdministrators(),
            b'{"type":"all_chat_administrators"}',
        ),
        (
            BotCommandScopeChat(123),
            b'{"type":"chat","chat_id":123}',
        ),
        (
            BotCommandScopeChatAdministrators(123),
            b'{"type":"chat_administrators","chat_id":123}',
        ),
        (
            BotCommandScopeChatMember(123, 456),
            b'{"type":"chat_member","chat_id":123,"user_id":456}',
        ),
    ),
)
def test_bot_command_scope(scope: BotCommandScope, json: bytes) -> None:
    assert msgspec.json.encode(scope) == json
