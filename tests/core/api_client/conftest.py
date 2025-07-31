from operator import itemgetter

import pytest
from litestar import Litestar, Request, Response, get
from litestar.handlers import HTTPRouteHandler

_STATE_T = dict[str, str | bytes]
_T = tuple[Litestar, _STATE_T]


@pytest.fixture
def setup() -> _T:
    state: _STATE_T = {}

    async def reg(request: Request) -> None:
        nonlocal state
        state["method"] = request.method
        state["body"] = await request.body()

    @HTTPRouteHandler("/url/", http_method=["GET", "OPTIONS", "PUT", "PATCH", "HEAD", "POST", "DELETE"])
    async def handler(request: Request) -> Response:
        await reg(request)
        return Response("Some text", status_code=200, media_type="text/plain")

    @get("/json_url/")
    async def json_handler(request: Request) -> Response:
        await reg(request)
        return Response({"key": "value"}, status_code=200, media_type="application/json")

    app = Litestar()
    app.register(handler)
    app.register(json_handler)

    return app, state


@pytest.fixture
def app(setup: _T) -> Litestar:
    return itemgetter(0)(setup)


@pytest.fixture
def req(setup: _T) -> _STATE_T:
    return itemgetter(1)(setup)
