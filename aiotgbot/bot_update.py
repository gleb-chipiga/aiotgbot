from typing import Any, Final, Iterator, MutableMapping

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

__all__ = (
    "BotUpdate",
    "Context",
)


class Context(MutableMapping[str, Any]):
    def __init__(self, data: dict[str, Any]) -> None:
        self._data: Final[dict[str, Any]] = data

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

    def clear(self) -> None:
        self._data.clear()

    def to_dict(self) -> dict[str, Any]:
        return self._data


class BotUpdate(MutableMapping[str, Any]):
    def __init__(
        self, state: str | None, context: Context, update: Update
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
