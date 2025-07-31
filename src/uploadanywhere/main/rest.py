import typing as t
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.litestar import (
    LitestarProvider,
    setup_dishka,
)
from litestar import Litestar

from uploadanywhere.presentation.rest_api.error_handlers import build_error_handlers
from uploadanywhere.presentation.rest_api.router import api_router

from .config import Config
from .ioc import AppProvider, CommandProcessorsProvider

config = Config()
container = make_async_container(
    LitestarProvider(),
    AppProvider(),
    CommandProcessorsProvider(),
    context={Config: config},
)


@asynccontextmanager
async def lifespan(app: Litestar) -> t.AsyncGenerator[None, None]:
    yield
    await app.state.dishka_container.close()


def create_base_app(debug: bool | None = None) -> Litestar:
    return Litestar(
        lifespan=[lifespan],
        route_handlers=[api_router],
        exception_handlers=build_error_handlers(),
        debug=debug,
    )


def create_app() -> Litestar:
    app = create_base_app()
    setup_dishka(container=container, app=app)
    return app


application = create_app()
