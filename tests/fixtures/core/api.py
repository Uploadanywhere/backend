import pytest
from httpx import ASGITransport, AsyncClient
from litestar import Litestar

from tests.core.api_client.api_client import ApiClient
from uploadanywhere.domain.entities.session import Session


@pytest.fixture
def api(app: Litestar, db_session: Session) -> ApiClient:
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")  # type: ignore[arg-type]
    client.headers.update({"session-id": str(db_session.id)})
    return ApiClient(httpx_client=client)


@pytest.fixture
def anon(app: Litestar) -> ApiClient:
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")  # type: ignore[arg-type]
    return ApiClient(httpx_client=client)
