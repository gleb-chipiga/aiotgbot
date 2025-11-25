"""Test configuration helpers."""

from __future__ import annotations

import os
import sys
import warnings
from collections.abc import AsyncIterator, Iterator
from importlib import import_module
from pathlib import Path
from types import TracebackType
from typing import Protocol, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def _ensure_src_on_path() -> None:
    """Prepend src/ to sys.path for installed-style imports."""

    src_path = Path(__file__).resolve().parents[1] / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


_ensure_src_on_path()

# Silence testcontainers deprecated decorator warning until we migrate.
warnings.filterwarnings(
    "ignore",
    message=r"The @wait_container_is_ready decorator is deprecated",
    category=DeprecationWarning,
)


class _PostgresContainerProto(Protocol):
    def __enter__(self) -> _PostgresContainerProto: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    def get_container_host_ip(self) -> str: ...
    def get_exposed_port(self, port: int | str) -> str: ...
    def get_connection_url(self) -> str: ...


class _PostgresContainerFactory(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> _PostgresContainerProto: ...


# Dynamically import testcontainers.postgres to avoid stub errors.
PostgresContainer: _PostgresContainerFactory = cast(
    _PostgresContainerFactory,
    import_module("testcontainers.postgres").PostgresContainer,
)


def _ensure_docker_host_env() -> None:
    """Set DOCKER_HOST to a reachable Docker socket.

    Tries rootless/Podman/Colima/classic paths; fails fast otherwise.
    """

    if os.environ.get("DOCKER_HOST"):
        # If it's a UNIX socket path, ensure it exists.
        docker_host = os.environ["DOCKER_HOST"]
        if (
            docker_host.startswith("unix://")
            and not Path(docker_host.removeprefix("unix://")).exists()
        ):
            raise RuntimeError(
                f"DOCKER_HOST is set to {docker_host} but socket is missing"
            )
        return

    uid = os.getuid()
    candidates = [
        f"unix:///run/user/{uid}/docker.sock",  # rootless Docker
        f"unix:///run/user/{uid}/podman/podman.sock",  # Podman Docker API
        f"unix://{Path.home()}/.colima/default/docker.sock",  # Colima
        "unix:///var/run/docker.sock",  # classic Docker
    ]

    tried: list[str] = []
    for url in candidates:
        sock_path = url.removeprefix("unix://")
        tried.append(sock_path)
        if Path(sock_path).exists():
            os.environ["DOCKER_HOST"] = url
            return

    paths = ", ".join(tried)
    msg = f"Docker socket not found; set DOCKER_HOST. Tried: {paths}"
    raise RuntimeError(msg)


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """Start Postgres in Docker and yield its asyncpg URL."""

    _ensure_docker_host_env()

    container = PostgresContainer(
        image="postgres:17-alpine",
        driver="asyncpg",
    )

    with container:
        yield container.get_connection_url()


@pytest.fixture
async def postgres_engine(postgres_url: str) -> AsyncIterator[AsyncEngine]:
    """Async SQLAlchemy engine for the live Postgres container."""

    engine = create_async_engine(postgres_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()
