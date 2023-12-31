from base64 import b64decode
from typing import AsyncIterator, Final, Self, Sequence, Union, cast

import msgspec.json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.constant_time import bytes_eq
from cryptography.hazmat.primitives.hashes import SHA1, SHA256, SHA512, Hash
from yarl import URL

from .api_types import API, EncryptedCredentials, PassportElementType

__all__ = (
    "Credentials",
    "DataCredentials",
    "FileCredentials",
    "IdDocumentData",
    "PassportCipher",
    "PassportKey",
    "PassportScope",
    "PassportScopeElement",
    "PassportScopeElementOne",
    "PassportScopeElementOneOfSeveral",
    "PersonalDetails",
    "ResidentialAddress",
    "SecureData",
    "SecureValue",
    "passport_request",
)


def passport_request(
    bot_id: int,
    scope: "PassportScope",
    public_key: str,
    nonce: str,
) -> str:
    url = URL("tg://resolve").with_query(
        domain="telegrampassport",
        bot_id=bot_id,
        scope=msgspec.json.encode(scope).decode(),
        public_key=public_key,
        nonce=nonce,
    )
    return str(url)


class PassportKey:
    _padding: Final[OAEP] = OAEP(
        mgf=MGF1(algorithm=SHA1()),
        algorithm=SHA1(),
        label=None,
    )

    def __init__(
        self,
        private_key: RSAPrivateKey,
    ) -> None:
        if not isinstance(private_key, RSAPrivateKey):
            raise RuntimeError("Key is not RSA private key")
        self._private_key: Final[RSAPrivateKey] = private_key
        public_key = self._private_key.public_key()
        public_bytes = public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self._public_key_pem: Final[str] = public_bytes.decode()

    @classmethod
    def load_der(
        cls,
        private_bytes: bytes,
    ) -> Self:
        private_key = serialization.load_der_private_key(
            private_bytes,
            password=None,
        )
        return cls(cast(RSAPrivateKey, private_key))

    @classmethod
    def load_pem(
        cls,
        private_text: str,
    ) -> Self:
        private_key = serialization.load_pem_private_key(
            private_text.encode(),
            password=None,
        )
        return cls(cast(RSAPrivateKey, private_key))

    def decrypt(
        self,
        ciphertext: bytes,
    ) -> bytes:
        return self._private_key.decrypt(ciphertext, self._padding)

    @property
    def public_key_pem(
        self,
    ) -> str:
        return self._public_key_pem


class PassportCipher:
    _key_size: Final[int] = 32
    _iv_size: Final[int] = 16

    def __init__(
        self,
        data_secret: bytes,
        data_hash: bytes,
    ) -> None:
        digest = Hash(SHA512())
        digest.update(data_secret)
        digest.update(data_hash)
        secret_hash = digest.finalize()
        key = secret_hash[: self._key_size]
        iv = secret_hash[
            self._key_size : self._key_size + self._iv_size  # noqa: E203
        ]
        self._data_hash: Final[bytes] = data_hash
        self._cipher: Final[Cipher[CBC]] = Cipher(AES(key), CBC(iv))

    def decrypt(
        self,
        ciphertext: bytes,
    ) -> bytes:
        decryptor = self._cipher.decryptor()
        assert isinstance(decryptor, CipherContext)
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        digest = Hash(SHA256())
        digest.update(plaintext)
        computed_hash = digest.finalize()
        if not bytes_eq(computed_hash, self._data_hash):
            raise RuntimeError("Decryption error")
        return plaintext[plaintext[0] :]  # noqa: E203

    async def decrypt_stream(
        self,
        stream: AsyncIterator[bytes],
    ) -> AsyncIterator[bytes]:
        decryptor = self._cipher.decryptor()
        assert isinstance(decryptor, CipherContext)
        digest = Hash(SHA256())
        skip = None
        async for chunk in stream:
            decrypted = decryptor.update(chunk)
            digest.update(decrypted)
            if skip is None:
                skip = decrypted[0]
            if skip >= len(decrypted):
                skip = skip - len(decrypted)
            else:
                yield decrypted[skip:]
                skip = 0
        decrypted = decryptor.finalize()
        digest.update(decrypted)
        computed_hash = digest.finalize()
        if not bytes_eq(computed_hash, self._data_hash):
            raise RuntimeError("Decryption error")
        yield decrypted[skip:]


class PassportScopeElementOne(API, frozen=True, kw_only=True):
    type: PassportElementType
    selfie: bool | None = None
    translation: bool | None = None
    native_names: bool | None = None


class PassportScopeElementOneOfSeveral(API, frozen=True, kw_only=True):
    one_of: Sequence[PassportScopeElementOne]
    selfie: bool | None = None
    translation: bool | None = None


PassportScopeElement = Union[
    PassportScopeElementOne,
    PassportScopeElementOneOfSeveral,
]


class PassportScope(
    API,
    frozen=True,
    tag_field="v",
    tag=1,
    kw_only=True,
):
    data: Sequence[PassportScopeElement]


class FileCredentials(API, frozen=True, kw_only=True):
    file_hash: str
    secret: str


class DataCredentials(API, frozen=True, kw_only=True):
    data_hash: str
    secret: str

    def decrypt(
        self,
        ciphertext: str,
    ) -> bytes:
        cipher = PassportCipher(
            b64decode(self.secret),
            b64decode(self.data_hash),
        )
        return cipher.decrypt(b64decode(ciphertext))


class SecureValue(API, frozen=True, kw_only=True):
    data: DataCredentials | None = None
    front_side: FileCredentials | None = None
    reverse_side: FileCredentials | None = None
    selfie: FileCredentials | None = None
    translation: Sequence[FileCredentials] | None = None
    files: Sequence[FileCredentials] | None = None


class SecureData(API, frozen=True, kw_only=True):
    personal_details: SecureValue | None = None
    passport: SecureValue | None = None
    internal_passport: SecureValue | None = None
    driver_license: SecureValue | None = None
    identity_card: SecureValue | None = None
    address: SecureValue | None = None
    utility_bill: SecureValue | None = None
    bank_statement: SecureValue | None = None
    rental_agreement: SecureValue | None = None
    passport_registration: SecureValue | None = None
    temporary_registration: SecureValue | None = None


class Credentials(API, frozen=True, kw_only=True):
    secure_data: SecureData
    nonce: str

    @classmethod
    def from_encrypted(
        cls,
        encrypted: EncryptedCredentials,
        passport_key: PassportKey,
    ) -> Self:
        data_secret = passport_key.decrypt(b64decode(encrypted.secret))
        data_hash = b64decode(encrypted.hash)
        ciphertext = b64decode(encrypted.data)
        cipher = PassportCipher(data_secret, data_hash)
        plaintext = cipher.decrypt(ciphertext)
        return msgspec.json.decode(plaintext, type=cls)


class PersonalDetails(API, frozen=True, kw_only=True):
    first_name: str
    last_name: str
    birth_date: str
    gender: str
    country_code: str
    residence_country_code: str
    middle_name: str | None = None
    first_name_native: str | None = None
    last_name_native: str | None = None
    middle_name_native: str | None = None


class ResidentialAddress(API, frozen=True, kw_only=True):
    street_line1: str
    city: str
    country_code: str
    post_code: str
    street_line2: str | None = None
    state: str | None = None


class IdDocumentData(API, frozen=True, kw_only=True):
    document_no: str
    expiry_date: str | None = None
