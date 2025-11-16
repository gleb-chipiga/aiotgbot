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
* `msgspec <https://github.com/jcrist/msgspec>`_
* `backoff <https://github.com/litl/backoff>`_
* `frozenlist <https://github.com/aio-libs/frozenlist>`_
* `aiofreqlimit <https://github.com/gleb-chipiga/aiofreqlimit>`_
* `yarl <https://github.com/aio-libs/yarl>`_

Using aiotgbot
==================

.. code-block:: python

    from typing import AsyncIterator

    from aiotgbot import (Bot, BotUpdate, BotUpdateKey, HandlerTable, PollBot,
                          PrivateChatFilter, Runner)
    from aiotgbot.storage_memory import MemoryStorage

    handlers = HandlerTable()


    @handlers.message(filters=[PrivateChatFilter()])
    async def reply_private_message(bot: Bot, update: BotUpdate) -> None:
        assert update.message is not None
        name = (f'{update.message.chat.first_name} '
                f'{update.message.chat.last_name}')
        update["greeting_count"] = update.get("greeting_count", 0) + 1
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

Upgrading to 0.18.0
===================

**New features:**

* **BotUpdateKey** - новый класс для типизированного хранения данных в ``BotUpdate``
* Новые методы ``BotUpdate``: ``get_typed(key)``, ``set_typed(key, value)``, ``del_typed(key)`` - для работы с ``BotUpdateKey``
* ``BotUpdateKey`` выполняет runtime проверку типов через ``isinstance()``

``BotUpdate`` remains a regular mutable mapping so filters and handlers can stash arbitrary helper objects between each other. To keep gopher data structured, use ``BotUpdateKey`` which enforces types per slot::

    from dataclasses import dataclass

    from aiotgbot import BotUpdateKey


    @dataclass
    class Session:
        trace_id: str
        retries: int


    session_key = BotUpdateKey("session", Session)


    async def my_handler(bot: Bot, update: BotUpdate) -> None:
        if session_key.name not in update:
            update.set_typed(session_key, Session(trace_id="abc", retries=0))
        session = update.get_typed(session_key)
        ...

Development
===========

We use `Prek <https://github.com/DetachHead/prek>`_ as a drop-in ``pre-commit`` replacement backed by ``uv`` so hook environments resolve quickly and reproducibly. Install it once and run the configured Ruff, ``mypy --strict``, and Basedpyright checks via:

.. code-block:: bash

    uv tool install prek
    prek install
    prek run --all-files

``prek run`` reads ``.pre-commit-config.yaml``, so you can still target a subset of hooks or files during local development.

``mise.toml`` at the repo root mirrors the common workflows, so you can rely on `mise <https://mise.jdx.dev/>`_ instead of remembering the raw commands. Trust the config once via ``mise trust mise.toml`` and then run, for example:

.. code-block:: bash

    mise run lint
    mise run mypy
    mise run basedpyright
    mise run test
