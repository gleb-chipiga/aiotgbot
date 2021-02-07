About
=====
Asynchronous library for Telegram bot API.

Installation
============
aiotgbot requires Python 3.8 or greater and is available on PyPI. Use pip to install it:

.. code-block:: bash

    pip install aiotgbot

Using aiotgbot
==================

.. code-block:: python

    from typing import AsyncIterator

    from aiotgbot import (Bot, BotUpdate, HandlerTable, PollBot,
                          PrivateChatFilter, Runner)
    from aiotgbot.storage_memory import MemoryStorage

    handlers = HandlerTable()


    @handlers.message(filters=[PrivateChatFilter()])
    async def reply_private_message(bot: Bot, update: BotUpdate) -> None:
        assert update.message is not None
        name = (f'{update.message.chat.first_name} '
                f'{update.message.chat.last_name}')
        await bot.send_message(update.message.chat.id, f'Hello, {name}!')


    async def run_context(runner: Runner) -> AsyncIterator[None]:
        storage = MemoryStorage()
        await storage.connect()
        handlers.freeze()
        bot = PollBot(runner['token'], handlers, storage)
        await bot.start()

        yield

        await bot.stop()
        await storage.close()


    def main() -> None:
        runner = Runner(run_context)
        runner['token'] = 'some:token'
        runner.run()


    if __name__ == '__main__':
        main()
