from typing import Any

import msgspec
import pytest
from msgspec import UNSET, Raw

from aiotgbot import API
from aiotgbot.api_types import APIResponse


class Result(API, frozen=True):
    a: int
    b: str
    c: bool


@pytest.mark.parametrize(
    "json,type_,result",
    (
        (b'{"ok": true, "result": true}', bool, True),
        (b'{"ok": true, "result": 11}', int, 11),
        (b'{"ok": true, "result": "text"}', str, "text"),
        (b'{"ok": true, "result": [1, 2, 3]}', tuple[int, ...], (1, 2, 3)),
        (b'{"ok": true, "result": null}', type(None), None),
        (b'{"ok": true, "result": 15}', int | None, 15),
        (b'{"ok": true, "result": null}', int | None, None),
        (
            b'{"ok": true, "result": {"a": 1, "b": "b", "c": false}}',
            Result,
            Result(a=1, b="b", c=False),
        ),
    ),
)
def test_api_response_ok(json: bytes, type_: Any, result: Any) -> None:
    api_response = msgspec.json.decode(json, type=APIResponse)
    assert api_response.ok is True
    assert isinstance(api_response.result, Raw)
    decoded_result = msgspec.json.decode(api_response.result, type=type_)
    assert decoded_result == result


def test_api_response_error() -> None:
    api_response = msgspec.json.decode(
        b'{"ok": false, "error_code": 10, "description": "some error"}',
        type=APIResponse,
    )
    assert api_response.ok is False
    assert api_response.result is UNSET
    assert api_response.error_code == 10
    assert api_response.description == "some error"
