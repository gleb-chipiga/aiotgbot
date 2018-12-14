from typing import Any, Dict, Iterator, MutableMapping, Optional

from .api_types import (CallbackQuery, ChosenInlineResult, InlineQuery,
                        Message, PreCheckoutQuery, ShippingQuery, Update)


class Context(MutableMapping[str, Any]):
    __slots__ = ('_data',)

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

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

    def reset(self) -> None:
        self._data = {}

    def to_dict(self) -> Dict[str, Any]:
        return self._data


class BotUpdate(MutableMapping[str, Any]):
    __slots__ = ('_state', '_context', '_update', '_data')

    def __init__(self, state: str, context: Context,
                 update: Update) -> None:
        self._state = state
        self._context = context
        self._update = update
        self._data: Dict[str, Any] = {}

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
    def state(self) -> Optional[str]:
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
    def message(self) -> Optional[Message]:
        return self._update.message

    @property
    def edited_message(self) -> Optional[Message]:
        return self._update.edited_message

    @property
    def channel_post(self) -> Optional[Message]:
        return self._update.channel_post

    @property
    def edited_channel_post(self) -> Optional[Message]:
        return self._update.edited_channel_post

    @property
    def inline_query(self) -> Optional[InlineQuery]:
        return self._update.inline_query

    @property
    def chosen_inline_result(self) -> Optional[ChosenInlineResult]:
        return self._update.chosen_inline_result

    @property
    def callback_query(self) -> Optional[CallbackQuery]:
        return self._update.callback_query

    @property
    def shipping_query(self) -> Optional[ShippingQuery]:
        return self._update.shipping_query

    @property
    def pre_checkout_query(self) -> Optional[PreCheckoutQuery]:
        return self._update.pre_checkout_query
