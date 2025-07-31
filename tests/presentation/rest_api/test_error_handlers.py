import pytest
from litestar import Litestar, Request, Response, status_codes
from litestar.handlers import HTTPRouteHandler

from tests.core.api_client.api_client import ApiClient
from uploadanywhere.application.exceptions import ApplicationError, NotAuthenticatedError
from uploadanywhere.domain.exceptions import AlreadyExistsError
from uploadanywhere.infrastructure.exceptions import UnauthorizedError


@pytest.fixture
def app(request: pytest.FixtureRequest, app: Litestar) -> Litestar:
    error = request.param.get("error", Exception)

    @HTTPRouteHandler(
        "/not_existing_url_for_test_error_handlers/",
        http_method=["GET", "OPTIONS", "PUT", "PATCH", "HEAD", "POST", "DELETE"],
    )
    async def json_handler(request: Request) -> Response:  # noqa: ARG001, RUF029
        if type(error) is Exception:
            raise error
        raise error("Test error")

    app.register(json_handler)
    app.debug = False

    return app


@pytest.mark.parametrize(
    ("app", "status_code", "error"),
    [
        ({"error": ApplicationError}, status_codes.HTTP_400_BAD_REQUEST, "server error"),
        ({"error": AlreadyExistsError}, status_codes.HTTP_409_CONFLICT, "User already exists"),
        ({"error": NotAuthenticatedError}, status_codes.HTTP_401_UNAUTHORIZED, "Authentication failed"),
        ({"error": UnauthorizedError}, status_codes.HTTP_401_UNAUTHORIZED, "Authentication failed"),
    ],
    indirect=["app"],
)
async def test_response_from_error_handlers(api: ApiClient, status_code: int, error: str) -> None:
    got = await api.get("/not_existing_url_for_test_error_handlers/", as_response=True)

    assert got.status_code == status_code
    assert got.headers["Content-Type"] == "application/json"
    got = got.json()
    assert got["detail"] == "Test error"
    assert got["error"] == error
    assert got["status_code"] == status_code
    assert got["path"] == "/not_existing_url_for_test_error_handlers"


@pytest.mark.parametrize(
    "app",
    [
        {"error": Exception},
    ],
    indirect=["app"],
)
async def test_response_from_error_handlers_unexpected_error(api: ApiClient) -> None:
    got = await api.get("/not_existing_url_for_test_error_handlers/", as_response=True)

    assert got.status_code == status_codes.HTTP_500_INTERNAL_SERVER_ERROR
    assert got.headers["Content-Type"] == "application/json"
    got = got.json()
    assert got["detail"] == "Internal Server Error"
    assert got["status_code"] == status_codes.HTTP_500_INTERNAL_SERVER_ERROR
