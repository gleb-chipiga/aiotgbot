from typing import Callable, Iterable, List, Optional

from .bot import (AbstractHandlerTable, BaseFilter, Bot, Handler,
                  HandlerCallable)
from .bot_update import BotUpdate
from .constants import ContentType, UpdateType
from .filters import (CallbackQueryDataFilter, CommandsFilter,
                      ContentTypeFilter, MessageTextFilter, StateFilter,
                      UpdateTypeFilter)

HandlerDecorator = Callable[[HandlerCallable], HandlerCallable]


class HandlerTable(AbstractHandlerTable):
    __slots__ = ('_handlers',)

    def __init__(self) -> None:
        self._handlers: List[Handler] = []

    def message_handler(
        self, handler: HandlerCallable,
        state: Optional[str] = None,
        commands: Optional[Iterable[str]] = None,
        content_types: Optional[Iterable[ContentType]] = None,
        text_match: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.MESSAGE)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if commands is not None:
            handler_filters.append(CommandsFilter(tuple(commands)))
        if content_types is not None:
            handler_filters.append(ContentTypeFilter(tuple(content_types)))
        if text_match is not None:
            handler_filters.append(MessageTextFilter(text_match))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def message(
        self, state: Optional[str] = None,
        commands: Optional[Iterable[str]] = None,
        content_types: Optional[Iterable[ContentType]] = None,
        text_match: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.message_handler(handler=handler, state=state,
                                 commands=commands,
                                 content_types=content_types,
                                 text_match=text_match, filters=filters)
            return handler
        return decorator

    def edited_message_handler(
        self, handler: HandlerCallable,
        state: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.EDITED_MESSAGE)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def edited_message(
        self, state: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.edited_message_handler(handler=handler, state=state,
                                        filters=filters)
            return handler
        return decorator

    def channel_post_handler(
        self, handler: HandlerCallable,
        state: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.CHANNEL_POST)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def channel_post(
        self, state: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.channel_post_handler(handler=handler, state=state,
                                      filters=filters)
            return handler
        return decorator

    def edited_channel_post_handler(
        self, handler: HandlerCallable,
        state: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.EDITED_CHANNEL_POST)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def edited_channel_post(
        self, state: Optional[str] = None,
        filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.edited_channel_post_handler(handler=handler, state=state,
                                             filters=filters)
            return handler
        return decorator

    def inline_query_handler(
            self, handler: HandlerCallable,
            state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.INLINE_QUERY)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def inline_query(
            self, state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.inline_query_handler(handler=handler, state=state,
                                      filters=filters)
            return handler
        return decorator

    def chosen_inline_result_handler(
            self, handler: HandlerCallable,
            state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.CHOSEN_INLINE_RESULT)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def chosen_inline_result(
            self, state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.chosen_inline_result_handler(handler=handler, state=state,
                                              filters=filters)
            return handler
        return decorator

    def callback_query_handler(
            self, handler: HandlerCallable,
            state: Optional[str] = None,
            data_match: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.CALLBACK_QUERY)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if data_match is not None:
            handler_filters.append(CallbackQueryDataFilter(data_match))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def callback_query(
            self, state: Optional[str] = None,
            data_match: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.callback_query_handler(handler=handler, state=state,
                                        data_match=data_match, filters=filters)
            return handler
        return decorator

    def shipping_query_handler(
            self, handler: HandlerCallable,
            state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.SHIPPING_QUERY)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def shipping_query(
            self, state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.shipping_query_handler(handler=handler, state=state,
                                        filters=filters)
            return handler
        return decorator

    def pre_checkout_query_handler(
            self, handler: HandlerCallable,
            state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> None:
        update_type_filter = UpdateTypeFilter(UpdateType.PRE_CHECKOUT_QUERY)
        handler_filters: List[BaseFilter] = [update_type_filter]
        if state is not None:
            handler_filters.append(StateFilter(state))
        if filters is not None:
            handler_filters.extend(filters)
        self._handlers.append(Handler(handler, tuple(handler_filters)))

    def pre_checkout_query(
            self, state: Optional[str] = None,
            filters: Optional[Iterable[BaseFilter]] = None
    ) -> HandlerDecorator:
        def decorator(handler: HandlerCallable) -> HandlerCallable:
            self.pre_checkout_query_handler(handler=handler, state=state,
                                            filters=filters)
            return handler
        return decorator

    async def get_handler(self, bot: Bot,
                          update: BotUpdate) -> Optional[HandlerCallable]:
        for handler in self._handlers:
            if await handler.check(bot, update):
                return handler.callable
        return None
