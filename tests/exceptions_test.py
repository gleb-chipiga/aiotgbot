from aiotgbot.exceptions import MigrateToChat, RetryAfter, TelegramError


def test_telegram_error_init() -> None:
    te = TelegramError(404, 'not found')

    assert te.error_code == 404
    assert te.description == 'not found'


def test_telegram_error_match() -> None:
    class SomeError(TelegramError):
        pattern = 'substring'

    assert not TelegramError.match('some string')
    assert SomeError.match('str substring str')
    assert not SomeError.match('str substr str')


def test_migrate_to_chat_init() -> None:
    mtc = MigrateToChat(400, 'migrate to chat', 1)

    assert mtc.error_code == 400
    assert mtc.description == 'migrate to chat'
    assert mtc.chat_id == 1


def test_retry_after_init() -> None:
    ra = RetryAfter(429, 'retry after', 10)

    assert ra.error_code == 429
    assert ra.description == 'retry after'
    assert ra.retry_after == 10
