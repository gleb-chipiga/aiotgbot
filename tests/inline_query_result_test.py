import msgspec
import pytest

from aiotgbot.api_types import (
    InlineQueryResult,
    InlineQueryResultArticle,
    InlineQueryResultAudio,
    InlineQueryResultCachedAudio,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedGif,
    InlineQueryResultCachedMpeg4Gif,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedSticker,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedVoice,
    InlineQueryResultContact,
    InlineQueryResultDocument,
    InlineQueryResultGame,
    InlineQueryResultGif,
    InlineQueryResultLocation,
    InlineQueryResultMpeg4Gif,
    InlineQueryResultPhoto,
    InlineQueryResultVenue,
    InlineQueryResultVideo,
    InlineQueryResultVoice,
    InputTextMessageContent,
)


@pytest.mark.parametrize(
    "inline_query_result,json",
    (
        (
            InlineQueryResultArticle("", "", InputTextMessageContent("")),
            b'{"type":"article","id":""',
        ),
        (
            InlineQueryResultPhoto("", "", ""),
            b'{"type":"photo","id":""',
        ),
        (
            InlineQueryResultGif("", "", ""),
            b'{"type":"gif","id":""',
        ),
        (
            InlineQueryResultMpeg4Gif("", "", ""),
            b'{"type":"mpeg4_gif","id":""',
        ),
        (
            InlineQueryResultVideo("", "", "", "", ""),
            b'{"type":"video","id":""',
        ),
        (
            InlineQueryResultAudio("", "", ""),
            b'{"type":"audio","id":""',
        ),
        (
            InlineQueryResultVoice("", "", ""),
            b'{"type":"voice","id":""',
        ),
        (
            InlineQueryResultDocument("", "", "", ""),
            b'{"type":"document","id":""',
        ),
        (
            InlineQueryResultLocation("", 0, 0, ""),
            b'{"type":"location","id":""',
        ),
        (
            InlineQueryResultVenue("", 0, 0, "", ""),
            b'{"type":"venue","id":""',
        ),
        (
            InlineQueryResultContact("", "", ""),
            b'{"type":"contact","id":""',
        ),
        (
            InlineQueryResultGame("", ""),
            b'{"type":"game","id":""',
        ),
        (
            InlineQueryResultCachedPhoto("", "", ""),
            b'{"type":"photo","id":""',
        ),
        (
            InlineQueryResultCachedGif("", "", ""),
            b'{"type":"gif","id":""',
        ),
        (
            InlineQueryResultCachedMpeg4Gif("", "", ""),
            b'{"type":"mpeg4_gif","id":""',
        ),
        (
            InlineQueryResultCachedSticker("", ""),
            b'{"type":"sticker","id":""',
        ),
        (
            InlineQueryResultCachedDocument("", "", "", ""),
            b'{"type":"document","id":""',
        ),
        (
            InlineQueryResultCachedVideo("", "", "", "", ""),
            b'{"type":"video","id":""',
        ),
        (
            InlineQueryResultCachedVoice("", "", ""),
            b'{"type":"voice","id":""',
        ),
        (
            InlineQueryResultCachedAudio("", "", ""),
            b'{"type":"audio","id":""',
        ),
    ),
)
def test_inline_query_result(
    inline_query_result: InlineQueryResult,
    json: bytes,
) -> None:
    assert msgspec.json.encode(inline_query_result).startswith(json)
