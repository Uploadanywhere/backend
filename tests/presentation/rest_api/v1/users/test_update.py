from litestar import status_codes

from tests.core.api_client.api_client import ApiClient
from tests.factories.users import UserFactory
from uploadanywhere.domain.entities.user import User


async def test_update_me(api: ApiClient, db_user: User, user_factory: UserFactory) -> None:
    got = await api.patch(
        "/api/v1/users/me",
        json={"username": "new_username"},
        as_response=True,
    )

    user = await user_factory.fetch_user(db_user.id)

    assert got.status_code == status_codes.HTTP_200_OK
    assert user["username"] == "new_username"


async def test_cannot_update_from_put_method(api: ApiClient) -> None:
    got = await api.put(
        "/api/v1/users/me",
        json={"username": "new_username"},
        as_response=True,
    )

    assert got.status_code == status_codes.HTTP_405_METHOD_NOT_ALLOWED


async def test_cannot_update_username_to_none(api: ApiClient, db_user: User, user_factory: UserFactory) -> None:
    got = await api.patch(
        "/api/v1/users/me",
        json={"username": None},
        as_response=True,
    )

    user = await user_factory.fetch_user(db_user.id)

    assert got.status_code == status_codes.HTTP_400_BAD_REQUEST
    assert user["username"] == db_user.username
