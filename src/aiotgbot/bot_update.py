import functools
from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass
from typing import Final, Generic, TypeVar

import msgspec
from typing_extensions import override  # Python 3.11 compatibility

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
    "BotUpdateKey",
    "Context",
    "ContextKey",
    "StateContext",
)


_T = TypeVar("_T")
_PayloadT = TypeVar("_PayloadT")


@functools.total_ordering
class ContextKey(Generic[_T]):
    __slots__: tuple[str, ...] = ("_name", "_type")

    def __init__(self, name: str, type_: type[_T]):
        self._name: Final = name
        self._type: Final[type[_T]] = type_

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> type[_T]:
        return self._type

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ContextKey):
            return self._name < other._name
        return True

    @override
    def __repr__(self) -> str:
        type_ = self._type
        module = getattr(type_, "__module__", None)
        qualname = getattr(type_, "__qualname__", None)
        if isinstance(module, str) and isinstance(qualname, str):
            t_repr = qualname if module == "builtins" else f"{module}.{qualname}"
        else:
            t_repr = repr(type_)
        return f"<ContextKey({self._name}, type={t_repr})>"


class Context(MutableMapping[str, Json]):
    def __init__(
        self,
        data: dict[str, Json],
    ) -> None:
        self._data: Final[dict[str, Json]] = data

    @override
    def __getitem__(self, key: str) -> Json:
        return self._data[key]

    @override
    def __setitem__(self, key: str, value: Json) -> None:
        self._data[key] = value

    @override
    def __delitem__(self, key: str) -> None:
        del self._data[key]

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    @override
    def clear(self) -> None:
        self._data.clear()

    def to_dict(self) -> dict[str, Json]:
        return self._data

    def get_typed(self, key: ContextKey[_T]) -> _T:
        return msgspec.convert(self._data[key.name], key.type)

    def set_typed(self, key: ContextKey[_T], value: _T) -> None:
        self._data[key.name] = msgspec.to_builtins(value)

    def del_typed(self, key: ContextKey[_T]) -> None:
        del self._data[key.name]


@dataclass
class StateContext:
    state: str | None
    context: Context


@functools.total_ordering
class BotUpdateKey(Generic[_T]):
    __slots__: tuple[str, ...] = ("_name", "_type")

    def __init__(self, name: str, type_: type[_T]):
        self._name: Final[str] = name
        self._type: Final[type[_T]] = type_

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> type[_T]:
        return self._type

    def __lt__(self, other: object) -> bool:
        if isinstance(other, BotUpdateKey):
            return self._name < other._name
        return True

    @override
    def __repr__(self) -> str:
        type_ = self._type
        module = getattr(type_, "__module__", None)
        qualname = getattr(type_, "__qualname__", None)
        if isinstance(module, str) and isinstance(qualname, str):
            t_repr = qualname if module == "builtins" else f"{module}.{qualname}"
        else:
            t_repr = repr(type_)
        return f"<BotUpdateKey({self._name}, type={t_repr})>"


class BotUpdate(MutableMapping[str, object]):
    def __init__(
        self,
        state: str | None,
        context: Context,
        update: Update,
    ) -> None:
        self._state: str | None = state
        self._context: Final[Context] = context
        self._update: Final[Update] = update
        self._data: Final[dict[str, object]] = {}

    @override
    def __getitem__(self, key: str) -> object:
        return self._data[key]

    @override
    def __setitem__(self, key: str, value: object) -> None:
        self._data[key] = value

    @override
    def __delitem__(self, key: str) -> None:
        del self._data[key]

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def get_typed(self, key: BotUpdateKey[_PayloadT]) -> _PayloadT:
        value = self._data[key.name]
        if not isinstance(value, key.type):
            expected = key.type.__qualname__
            actual = type(value).__qualname__
            message = (
                f'BotUpdateKey "{key.name}" expected value of type '
                f"{expected}, got {actual}"
            )
            raise TypeError(message)
        return value

    def set_typed(self, key: BotUpdateKey[_PayloadT], value: _PayloadT) -> None:
        if not isinstance(value, key.type):
            expected = key.type.__qualname__
            actual = type(value).__qualname__
            message = (
                f'BotUpdateKey "{key.name}" expected type {expected}, got {actual}'
            )
            raise TypeError(message)
        self._data[key.name] = value

    def del_typed(self, key: BotUpdateKey[_PayloadT]) -> None:
        del self._data[key.name]

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
