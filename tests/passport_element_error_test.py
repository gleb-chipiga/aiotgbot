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
                PassportElementDataType.PASSPORT, "", "", ""
            ),
            b'{"source":"data","type":"passport"',
        ),
        (
            PassportElementErrorFrontSide(
                PassportElementFrontSideType.PASSPORT, "", ""
            ),
            b'{"source":"front_side","type":"passport"',
        ),
        (
            PassportElementErrorReverseSide(
                PassportElementReverseSideType.IDENTITY_CARD, "", ""
            ),
            b'{"source":"reverse_side","type":"identity_card"',
        ),
        (
            PassportElementErrorSelfie(
                PassportElementSelfieType.PASSPORT, "", ""
            ),
            b'{"source":"selfie","type":"passport"',
        ),
        (
            PassportElementErrorFile(
                PassportElementFileType.UTILITY_BILL, "", ""
            ),
            b'{"source":"file","type":"utility_bill"',
        ),
        (
            PassportElementErrorFiles(
                PassportElementFileType.UTILITY_BILL, "", ""
            ),
            b'{"source":"files","type":"utility_bill"',
        ),
        (
            PassportElementErrorTranslationFile(
                PassportElementTranslationFileType.PASSPORT, "", ""
            ),
            b'{"source":"translation_file","type":"passport"',
        ),
        (
            PassportElementErrorTranslationFiles(
                PassportElementTranslationFileType.PASSPORT, "", ""
            ),
            b'{"source":"translation_files","type":"passport"',
        ),
        (
            PassportElementErrorUnspecified(
                PassportElementType.PASSPORT, "", ""
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
