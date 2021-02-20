import asyncio
from hmac import compare_digest
from ipaddress import IPv4Address, IPv4Network
from secrets import token_urlsafe
from typing import Any, Awaitable, Callable, Final, Optional, Tuple, Union

from aiohttp import BaseConnector
from aiohttp.web import (Application, HTTPInternalServerError, HTTPNotFound,
                         Request, Response, StreamResponse, middleware)
from yarl import URL

from .api_types import InputFile, Update
from .bot import Bot, HandlerTableProtocol
from .storage import StorageProtocol

NETWORKS: Final[Tuple[IPv4Network, ...]] = (IPv4Network('149.154.160.0/20'),
                                            IPv4Network('91.108.4.0/22'))
WEBHOOK_TOKEN_SIZE: Final[int] = 32


class ListenBot(Bot):

    def __init__(
        self,
        url: Union[str, URL],
        token: str,
        handler_table: 'HandlerTableProtocol',
        storage: StorageProtocol,
        certificate: Optional[InputFile] = None,
        ip_address: Optional[str] = None,
        connector: Optional[BaseConnector] = None,
        check_remote_address: bool = False,
        **application_args: Any
    ) -> None:
        super().__init__(token, handler_table, storage, connector)
        self._url: URL = URL(url) if isinstance(url, str) else url
        self._certificate = certificate
        self._ip_address = ip_address
        self._webhook_token: Optional[str] = None
        middlewares = []
        if check_remote_address:
            middlewares.append(self._check_remote_address)
        if 'middlewares' in application_args:
            middlewares.extend(application_args.pop('middlewares'))
        if 'router' in application_args:
            raise RuntimeError('"Router" application arg is not supported')
        self._application = Application(middlewares=middlewares,
                                        **application_args)
        self._application.router.add_post('/{token}', self._handler)

    @property
    def application(self) -> Application:
        return self._application

    @middleware
    async def _check_remote_address(
        self, request: Request,
        handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        address = IPv4Address(request.remote)
        if not any(address in network for network in NETWORKS):
            raise HTTPNotFound()
        return await handler(request)

    async def _handler(self, request: Request) -> StreamResponse:
        if not self._started:
            raise HTTPInternalServerError()
        assert self._scheduler is not None
        assert self._webhook_token is not None
        if not compare_digest(self._webhook_token,
                              request.match_info['token']):
            raise HTTPNotFound()
        update = Update.from_dict(await request.json())
        await self._scheduler.spawn(self._handle_update(update))
        return Response()

    async def start(self) -> None:
        if self._started:
            raise RuntimeError('Polling already started')
        await self._start()
        loop = asyncio.get_running_loop()
        self._webhook_token = await loop.run_in_executor(
            None, token_urlsafe, WEBHOOK_TOKEN_SIZE)
        assert isinstance(self._webhook_token, str)
        url = str(self._url / self._webhook_token)
        await self.set_webhook(url, self._certificate, self._ip_address)

    async def stop(self) -> None:
        if not self._started:
            raise RuntimeError('Polling not started')
        if self._stopped:
            raise RuntimeError('Polling already stopped')
        self._stopped = True
        await self.delete_webhook()
        await self._cleanup()
