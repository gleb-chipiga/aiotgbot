import msgspec
import pytest

from aiotgbot.api_types import (
    InputMedia,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)


@pytest.mark.parametrize(
    "input_media,json",
    (
        (
            InputMediaPhoto(media="media"),
            b'{"type":"photo","media":"media"}',
        ),
        (
            InputMediaVideo(media="media"),
            b'{"type":"video","media":"media"}',
        ),
        (
            InputMediaAnimation(media="media"),
            b'{"type":"animation","media":"media"}',
        ),
        (
            InputMediaAudio(media="media"),
            b'{"type":"audio","media":"media"}',
        ),
        (
            InputMediaDocument(media="media"),
            b'{"type":"document","media":"media"}',
        ),
    ),
)
def test_input_media(input_media: InputMedia, json: bytes) -> None:
    assert msgspec.json.encode(input_media) == json
