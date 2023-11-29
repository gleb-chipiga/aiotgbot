from io import BytesIO
from tempfile import TemporaryDirectory
from typing import Any

import msgspec
import pytest

from aiotgbot.api_types import (
    InputMedia,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    LocalFile,
)


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
        msgspec.to_builtins(input_media)


@pytest.mark.parametrize("count", (2**10, 2**16))
@pytest.mark.asyncio
async def test_local_file(count: int) -> None:
    with TemporaryDirectory() as tmpdirname:
        file_name = f"{tmpdirname}/file.tmp"
        with open(file_name, "wb") as writer:
            for _ in range(count):
                writer.write(b"bytes")

        file = LocalFile(file_name)
        assert file.name == "file.tmp"
        assert file.content_type is None
        content = b""
        async for chunk in file.content:
            content += chunk

        assert content == b"bytes" * count
