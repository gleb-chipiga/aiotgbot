=========================================
Asynchronous library for Telegram bot API
=========================================

.. image:: https://badge.fury.io/py/aiotgbot.svg
   :target: https://pypi.org/project/aiotgbot
   :alt: Latest PyPI package version

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/gleb-chipiga/aiotgbot/blob/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/pypi/dm/aiotgbot
   :target: https://pypistats.org/packages/aiotgbot
   :alt: Downloads count

Key Features
============

* Asyncio and `aiohttp <https://github.com/aio-libs/aiohttp>`_ based
* All `Telegram Bot API <https://core.telegram.org/bots/api>`_ types and methods supported
* Bot API rate limit support
* Both long polling and webhooks supported
* Fully type annotated (`PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_)

Installation
============
aiotgbot is available on PyPI. Use pip to install it:

.. code-block:: bash

    pip install aiotgbot

Requirements
============

* Python >= 3.8
* `aiohttp <https://github.com/aio-libs/aiohttp>`_
* `aiojobs <https://github.com/aio-libs/aiojobs>`_
* `attrs <https://github.com/python-attrs/attrs>`_
* `backoff <https://github.com/litl/backoff>`_
* `frozenlist <https://github.com/aio-libs/frozenlist>`_
* `aiofreqlimit <https://github.com/gleb-chipiga/aiofreqlimit>`_
* `yarl <https://github.com/aio-libs/yarl>`_

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
