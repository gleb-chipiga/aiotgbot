import re
from typing import Tuple

import attr

from .bot import BaseFilter, Bot
from .bot_update import BotUpdate
from .constants import ChatType, ContentType, UpdateType


@attr.s(slots=True, frozen=True, auto_attribs=True)
class UpdateTypeFilter(BaseFilter):
    update_type: UpdateType

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return getattr(update, self.update_type.value) is not None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class StateFilter(BaseFilter):
    state: str

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return update.state == self.state


@attr.s(slots=True, frozen=True, auto_attribs=True)
class CommandsFilter(BaseFilter):
    commands: Tuple[str, ...]

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        if update.message is None or update.message.text is None:
            return False
        if any(update.message.text.startswith(f'/{command}')
               for command in self.commands):
            return True
        return False


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ContentTypeFilter(BaseFilter):
    content_types: Tuple[ContentType, ...]

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
            if getattr(message, content_type.value) is not None:
                return True
        return False


@attr.s(slots=True, frozen=True, auto_attribs=True)
class MessageTextFilter(BaseFilter):
    pattern: re.Pattern

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return (update.message is not None and
                update.message.text is not None and
                self.pattern.match(update.message.text) is not None)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class CallbackQueryDataFilter(BaseFilter):
    pattern: re.Pattern

    async def check(self, bot: Bot, update: BotUpdate) -> bool:

        return (update.callback_query is not None and
                update.callback_query.data is not None and
                self.pattern.match(update.callback_query.data) is not None)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PrivateChatFilter(BaseFilter):

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return (update.message is not None and
                update.message.chat is not None and
                update.message.chat.type == ChatType.PRIVATE)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class GroupChatFilter(BaseFilter):

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        group_types = (ChatType.GROUP, ChatType.SUPERGROUP)
        return (update.message is not None and
                update.message.chat is not None and
                update.message.chat.type in group_types)
