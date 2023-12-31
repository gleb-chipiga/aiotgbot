import msgspec
import pytest

from aiotgbot.api_types import (
    PassportElementDataType,
    PassportElementError,
    PassportElementErrorDataField,
    PassportElementErrorFile,
    PassportElementErrorFiles,
    PassportElementErrorFrontSide,
    PassportElementErrorReverseSide,
    PassportElementErrorSelfie,
    PassportElementErrorTranslationFile,
    PassportElementErrorTranslationFiles,
    PassportElementErrorUnspecified,
    PassportElementFileType,
    PassportElementFrontSideType,
    PassportElementReverseSideType,
    PassportElementSelfieType,
    PassportElementTranslationFileType,
    PassportElementType,
)


@pytest.mark.parametrize(
    "passport_element_error,json",
    (
        (
            PassportElementErrorDataField(
                type=PassportElementDataType.PASSPORT,
                field_name="",
                data_hash="",
                message="",
            ),
            b'{"source":"data","type":"passport"',
        ),
        (
            PassportElementErrorFrontSide(
                type=PassportElementFrontSideType.PASSPORT,
                file_hash="",
                message="",
            ),
            b'{"source":"front_side","type":"passport"',
        ),
        (
            PassportElementErrorReverseSide(
                type=PassportElementReverseSideType.IDENTITY_CARD,
                file_hash="",
                message="",
            ),
            b'{"source":"reverse_side","type":"identity_card"',
        ),
        (
            PassportElementErrorSelfie(
                type=PassportElementSelfieType.PASSPORT,
                file_hash="",
                message="",
            ),
            b'{"source":"selfie","type":"passport"',
        ),
        (
            PassportElementErrorFile(
                type=PassportElementFileType.UTILITY_BILL,
                file_hash="",
                message="",
            ),
            b'{"source":"file","type":"utility_bill"',
        ),
        (
            PassportElementErrorFiles(
                type=PassportElementFileType.UTILITY_BILL,
                file_hashes="",
                message="",
            ),
            b'{"source":"files","type":"utility_bill"',
        ),
        (
            PassportElementErrorTranslationFile(
                type=PassportElementTranslationFileType.PASSPORT,
                file_hash="",
                message="",
            ),
            b'{"source":"translation_file","type":"passport"',
        ),
        (
            PassportElementErrorTranslationFiles(
                type=PassportElementTranslationFileType.PASSPORT,
                file_hashes=("",),
                message="",
            ),
            b'{"source":"translation_files","type":"passport"',
        ),
        (
            PassportElementErrorUnspecified(
                type=PassportElementType.PASSPORT,
                element_hash="",
                message="",
            ),
            b'{"source":"unspecified","type":"passport"',
        ),
    ),
)
def test_input_media(
    passport_element_error: PassportElementError,
    json: bytes,
) -> None:
    assert isinstance(passport_element_error, PassportElementError)
    assert msgspec.json.encode(passport_element_error).startswith(json)
