from typing import ClassVar

__all__ = (
    "BadGateway",
    "BotBlocked",
    "BotKicked",
    "ChatNotFound",
    "MigrateToChat",
    "RestartingTelegram",
    "RetryAfter",
    "TelegramError",
)


class TelegramError(Exception):
    pattern: ClassVar[str | None] = None

    def __init__(self, error_code: int, description: str) -> None:
        super().__init__(f"{error_code} {description}")
        self.error_code: int = error_code
        self.description: str = description

    @classmethod
    def match(cls, description: str) -> bool:
        return cls.pattern is not None and cls.pattern in description.lower()


class MigrateToChat(TelegramError):  # noqa: N818 - Telegram API naming
    def __init__(self, error_code: int, description: str, chat_id: int) -> None:
        super().__init__(error_code, description)
        self.chat_id: int = chat_id


class RetryAfter(TelegramError):  # noqa: N818 - Telegram API naming
    def __init__(self, error_code: int, description: str, retry_after: int) -> None:
        super().__init__(error_code, description)
        self.retry_after: int = retry_after


class BadGateway(TelegramError):  # noqa: N818 - Telegram API naming
    pattern: ClassVar[str | None] = "bad gateway"


class RestartingTelegram(TelegramError):  # noqa: N818 - Telegram API naming
    pattern: ClassVar[str | None] = "restart"


class BotBlocked(TelegramError):  # noqa: N818 - Telegram API naming
    pattern: ClassVar[str | None] = "bot was blocked by the user"


class BotKicked(TelegramError):  # noqa: N818 - Telegram API naming
    pattern: ClassVar[str | None] = "bot was kicked from a chat"


class ChatNotFound(TelegramError):  # noqa: N818 - Telegram API naming
    pattern: ClassVar[str | None] = "chat not found"
