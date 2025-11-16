import re
from dataclasses import dataclass
from typing import ClassVar, Final

from typing_extensions import override  # Python 3.11 compatibility

from .bot import Bot, FilterProtocol
from .bot_update import BotUpdate
from .constants import ChatType, ContentType, UpdateType

__all__ = (
    "ANDFilter",
    "CallbackQueryDataFilter",
    "CommandsFilter",
    "ContentTypeFilter",
    "GroupChatFilter",
    "MessageTextFilter",
    "NOTFilter",
    "ORFilter",
    "PrivateChatFilter",
    "StateFilter",
    "UpdateTypeFilter",
)


@dataclass(frozen=True)
class UpdateTypeFilter(FilterProtocol):
    update_type: UpdateType

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return getattr(update, self.update_type) is not None


@dataclass(frozen=True)
class StateFilter(FilterProtocol):
    state: str

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return update.state == self.state


@dataclass(frozen=True)
class CommandsFilter(FilterProtocol):
    commands: tuple[str, ...]

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        if update.message is None or update.message.text is None:
            return False
        return any(
            update.message.text.startswith(f"/{command}") for command in self.commands
        )


@dataclass(frozen=True)
class ContentTypeFilter(FilterProtocol):
    content_types: tuple[ContentType, ...]

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        if update.message is not None:
            message = update.message
        elif update.edited_message is not None:
            message = update.edited_message
        elif update.channel_post is not None:
            message = update.channel_post
        elif update.edited_channel_post is not None:
            message = update.edited_channel_post
        else:
            return False
        for content_type in self.content_types:
            if getattr(message, content_type) is not None:
                return True
        return False


@dataclass(frozen=True)
class MessageTextFilter(FilterProtocol):
    pattern: "re.Pattern[str]"

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return (
            update.message is not None
            and update.message.text is not None
            and self.pattern.match(update.message.text) is not None
        )


@dataclass(frozen=True)
class CallbackQueryDataFilter(FilterProtocol):
    pattern: "re.Pattern[str]"

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return (
            update.callback_query is not None
            and update.callback_query.data is not None
            and self.pattern.match(update.callback_query.data) is not None
        )


@dataclass(frozen=True)
class PrivateChatFilter(FilterProtocol):
    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return (
            (
                update.message is not None
                and update.message.chat.type == ChatType.PRIVATE
            )
            or (
                update.callback_query is not None
                and update.callback_query.message is not None
                and update.callback_query.message.chat.type == ChatType.PRIVATE
            )
            or (
                update.my_chat_member is not None
                and update.my_chat_member.chat.type == ChatType.PRIVATE
            )
        )


@dataclass(frozen=True)
class GroupChatFilter(FilterProtocol):
    __group_types: ClassVar = (ChatType.GROUP, ChatType.SUPERGROUP)

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return (
            (
                update.message is not None
                and update.message.chat.type in self.__group_types
            )
            or (
                update.callback_query is not None
                and update.callback_query.message is not None
                and update.callback_query.message.chat.type in self.__group_types
            )
            or (
                update.my_chat_member is not None
                and update.my_chat_member.chat.type in self.__group_types
            )
        )


class ORFilter(FilterProtocol):
    def __init__(self, *filters: FilterProtocol) -> None:
        self._filters: Final = filters

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        for filter_item in self._filters:
            if await filter_item.check(bot, update):
                return True
        return False


class ANDFilter(FilterProtocol):
    def __init__(self, *filters: FilterProtocol) -> None:
        self._filters: Final = filters

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        for filter_item in self._filters:
            if not await filter_item.check(bot, update):
                return False
        return True


class NOTFilter(FilterProtocol):
    def __init__(self, filters: FilterProtocol) -> None:
        self._filter: Final = filters

    @override
    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return not await self._filter.check(bot, update)
