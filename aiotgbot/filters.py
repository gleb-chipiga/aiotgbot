import re
from dataclasses import dataclass
from typing import Final

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
    "ORFilter",
    "PrivateChatFilter",
    "StateFilter",
    "UpdateTypeFilter",
)


@dataclass(frozen=True)
class UpdateTypeFilter:
    update_type: UpdateType

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return getattr(update, self.update_type) is not None


@dataclass(frozen=True)
class StateFilter:
    state: str

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return update.state == self.state


@dataclass(frozen=True)
class CommandsFilter:
    commands: tuple[str, ...]

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        if update.message is None or update.message.text is None:
            return False
        if any(
            update.message.text.startswith(f"/{command}")
            for command in self.commands
        ):
            return True
        return False


@dataclass(frozen=True)
class ContentTypeFilter:
    content_types: tuple[ContentType, ...]

    async def check(self, _: Bot, update: BotUpdate) -> bool:
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
class MessageTextFilter:
    pattern: "re.Pattern[str]"

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return (
            update.message is not None
            and update.message.text is not None
            and self.pattern.match(update.message.text) is not None
        )


@dataclass(frozen=True)
class CallbackQueryDataFilter:
    pattern: "re.Pattern[str]"

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return (
            update.callback_query is not None
            and update.callback_query.data is not None
            and self.pattern.match(update.callback_query.data) is not None
        )


@dataclass(frozen=True)
class PrivateChatFilter:
    async def check(self, _: Bot, update: BotUpdate) -> bool:  # noqa
        return (
            update.message is not None
            and update.message.chat is not None
            and update.message.chat.type == ChatType.PRIVATE
        )


@dataclass(frozen=True)
class GroupChatFilter:
    async def check(self, _: Bot, update: BotUpdate) -> bool:  # noqa
        group_types = (ChatType.GROUP, ChatType.SUPERGROUP)
        return (
            update.message is not None
            and update.message.chat is not None
            and update.message.chat.type in group_types
        )


class ORFilter:
    def __init__(self, *filters: FilterProtocol) -> None:
        self._filters: Final[tuple[FilterProtocol, ...]] = filters

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        for filter_item in self._filters:
            if await filter_item.check(bot, update):
                return True
        return False


class ANDFilter:
    def __init__(self, *filters: FilterProtocol) -> None:
        self._filters: Final[tuple[FilterProtocol, ...]] = filters

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        for filter_item in self._filters:
            if not await filter_item.check(bot, update):
                return False
        return True
