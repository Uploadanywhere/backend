from litestar import status_codes

from tests.core.api_client.api_client import ApiClient


async def test_work_my_workspaces_endpoint(api: ApiClient) -> None:
    await api.get("/api/v1/workspaces", expected_status=status_codes.HTTP_200_OK)


async def test_anon_cant_get_info_any_workspace(anon: ApiClient) -> None:
    response = await anon.get("/api/v1/workspaces", as_response=True)

    assert response.status_code == status_codes.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Unauthorized"
