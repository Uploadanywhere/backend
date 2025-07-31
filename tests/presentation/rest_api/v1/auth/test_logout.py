import pytest
from litestar import status_codes

from tests.core.api_client.api_client import ApiClient
from tests.factories.sessions import SessionFactory


async def test_logout(api: ApiClient, session_factory: SessionFactory) -> None:
    await api.post(
        "/api/v1/auth/logout/",
        expected_status=status_codes.HTTP_204_NO_CONTENT,
    )

    assert await session_factory.count_sessions() == 0


async def test_after_logout_cookie_unset(api: ApiClient) -> None:
    response = await api.post(
        "/api/v1/auth/logout/",
        as_response=True,
    )

    assert response.cookies == {}


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
async def test_logout_works_only_for_post_request(api: ApiClient, method: str) -> None:
    await getattr(api, method)(
        "/api/v1/auth/logout/",
        expected_status=status_codes.HTTP_405_METHOD_NOT_ALLOWED,
    )
