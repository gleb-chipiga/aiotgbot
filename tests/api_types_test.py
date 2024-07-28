from io import BytesIO
from tempfile import TemporaryDirectory
from typing import Any, AsyncIterator

import pytest
from more_itertools import ichunked

from aiotgbot import ChatType
from aiotgbot.api_types import (
    API,
    InputFile,
    InputMedia,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    LocalFile,
    StreamFile,
    Message,
    Chat,
)


def test_to_builtins() -> None:
    class XYZ(API, frozen=True, kw_only=True):
        a: int
        b: str

    xyz = XYZ(a=1, b="2")

    assert xyz.to_builtins() == {"a": 1, "b": "2"}


def test_convert() -> None:
    class XYZ(API, frozen=True, kw_only=True):
        a: int
        b: str

    assert XYZ.convert({"a": 1, "b": "2"}) == XYZ(a=1, b="2")


@pytest.mark.skip("need refactoring")
@pytest.mark.parametrize(
    "type_",
    (
        InputMedia,
        InputMediaPhoto,
        InputMediaVideo,
        InputMediaAnimation,
        InputMediaAudio,
        InputMediaDocument,
    ),
)
def test_input_media_serialization(type_: Any) -> None:
    input_media = type_(media=BytesIO(b"bytes"))
    with pytest.raises(
        TypeError,
        match="Encoding objects of type _io.BytesIO is unsupported",
    ):
        input_media.to_builtins()


async def check_input_file(
    file: InputFile,
    expected_name: str,
    expected_content_type: str | None,
    expected_content: bytes,
) -> None:
    assert isinstance(file, InputFile)
    assert file.name == expected_name
    assert file.content_type == expected_content_type
    actual_content = bytearray()
    async for chunk in file.content:
        actual_content.extend(chunk)
    assert actual_content == expected_content


@pytest.mark.parametrize("count", (2**10, 2**16))
@pytest.mark.asyncio
async def test_local_file(count: int) -> None:
    with TemporaryDirectory() as tmpdirname:
        file_name = f"{tmpdirname}/file.tmp"
        with open(file_name, "wb") as writer:
            for _ in range(count):
                writer.write(b"bytes")
        file = LocalFile(file_name)
        await check_input_file(
            file,
            "file.tmp",
            None,
            b"bytes" * count,
        )


@pytest.mark.parametrize("count", (2**10, 2**16))
@pytest.mark.asyncio
async def test_stream_file(count: int) -> None:
    async def content() -> AsyncIterator[bytes]:
        for chunk in ichunked(b"bytes" * count, 32):
            yield bytes(chunk)

    file = StreamFile(
        name="file.txt",
        content=content(),
        content_type="text/plain",
    )
    await check_input_file(
        file,
        "file.txt",
        "text/plain",
        b"bytes" * count,
    )


@pytest.mark.parametrize(
    "date,is_inaccessible",
    (
        (0, True),
        (1, False),
    ),
)
async def test_message(date, is_inaccessible) -> None:
    message = Message(
        message_id=1,
        date=date,
        chat=Chat(
            id=1,
            type=ChatType.PRIVATE,
        ),
    )
    assert message.is_inaccessible is is_inaccessible
