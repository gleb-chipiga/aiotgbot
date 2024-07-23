import functools
from contextlib import suppress
from dataclasses import dataclass
from typing import (
    Any,
    Final,
    Generic,
    Iterator,
    MutableMapping,
    Type,
    TypeVar,
    get_args,
)

import msgspec

from .api_types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Poll,
    PollAnswer,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
)
from .helpers import Json

__all__ = (
    "BotUpdate",
    "Context",
    "ContextKey",
    "StateContext",
)


_T = TypeVar("_T")


@functools.total_ordering
class ContextKey(Generic[_T]):
    __slots__ = ("_name", "_type", "__orig_class__")
    __orig_class__: Type[object]

    def __init__(self, name: str, type_: Type[_T]):
        self._name: Final = name
        self._type: Final = type_

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> Type[_T]:
        return self._type

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ContextKey):
            return self._name < other._name
        return True

    def __repr__(self) -> str:
        type_ = self._type
        if type_ is None:
            with suppress(AttributeError):
                type_ = get_args(self.__orig_class__)[0]
        if type_ is None:
            t_repr = "<<Unknown>>"
        elif isinstance(type_, type):
            if type_.__module__ == "builtins":
                t_repr = type_.__qualname__
            else:
                t_repr = f"{type_.__module__}.{type_.__qualname__}"
        else:
            t_repr = repr(type_)
        return f"<ContextKey({self._name}, type={t_repr})>"


class Context(MutableMapping[str, Json]):
    def __init__(
        self,
        data: dict[str, Json],
    ) -> None:
        self._data: Final[dict[str, Json]] = data

    def __getitem__(self, key: str) -> Json:
        return self._data[key]

    def __setitem__(self, key: str, value: Json) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def clear(self) -> None:
        self._data.clear()

    def to_dict(self) -> dict[str, Json]:
        return self._data

    def get_typed(self, key: ContextKey[_T]) -> _T:
        return msgspec.convert(self._data[key.name], key.type)

    def set_typed(self, key: ContextKey[_T], value: _T) -> None:
        self._data[key.name] = msgspec.to_builtins(value)

    def del_typed(self, key: ContextKey[Any]) -> None:
        del self._data[key.name]


@dataclass
class StateContext:
    state: str | None
    context: Context


class BotUpdate(MutableMapping[str, Any]):
    def __init__(
        self,
        state: str | None,
        context: Context,
        update: Update,
    ) -> None:
        self._state: str | None = state
        self._context: Final[Context] = context
        self._update: Final[Update] = update
        self._data: Final[dict[str, Any]] = {}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    @property
    def state(self) -> str | None:
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        self._state = value

    @property
    def context(self) -> Context:
        return self._context

    @property
    def update_id(self) -> int:
        return self._update.update_id

    @property
    def message(self) -> Message | None:
        return self._update.message

    @property
    def edited_message(self) -> Message | None:
        return self._update.edited_message

    @property
    def channel_post(self) -> Message | None:
        return self._update.channel_post

    @property
    def edited_channel_post(self) -> Message | None:
        return self._update.edited_channel_post

    @property
    def inline_query(self) -> InlineQuery | None:
        return self._update.inline_query

    @property
    def chosen_inline_result(self) -> ChosenInlineResult | None:
        return self._update.chosen_inline_result

    @property
    def callback_query(self) -> CallbackQuery | None:
        return self._update.callback_query

    @property
    def shipping_query(self) -> ShippingQuery | None:
        return self._update.shipping_query

    @property
    def pre_checkout_query(self) -> PreCheckoutQuery | None:
        return self._update.pre_checkout_query

    @property
    def poll(self) -> Poll | None:
        return self._update.poll

    @property
    def poll_answer(self) -> PollAnswer | None:
        return self._update.poll_answer

    @property
    def my_chat_member(self) -> ChatMemberUpdated | None:
        return self._update.my_chat_member

    @property
    def chat_member(self) -> ChatMemberUpdated | None:
        return self._update.chat_member
