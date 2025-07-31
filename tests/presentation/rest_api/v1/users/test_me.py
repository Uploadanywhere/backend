from litestar import status_codes

from tests.core.api_client.api_client import ApiClient
from uploadanywhere.domain.entities.user import User


async def test_me(api: ApiClient, db_user: User) -> None:
    response = await api.get("/api/v1/users/me")

    assert response == {"id": str(db_user.id)}


async def test_anon_cant_get_info_about_himself(anon: ApiClient) -> None:
    response = await anon.get("/api/v1/users/me", as_response=True)

    assert response.status_code == status_codes.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Unauthorized"
