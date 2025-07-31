from http.cookies import SimpleCookie

import pytest
from dishka import AsyncContainer
from litestar import status_codes
from uuid6 import UUID, uuid7

from tests.core.api_client.api_client import ApiClient
from tests.factories.sessions import SessionFactory
from tests.factories.users import UserFactory
from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import UserId

_UserID: UUID = uuid7()


@pytest.fixture(autouse=True)
async def user(user_factory: UserFactory, container: AsyncContainer, rs_container: AsyncContainer) -> None:
    password_hasher = await container.get(PasswordHasher)
    uow = await rs_container.get(AsyncUoW)
    await user_factory.create_user(
        User(
            user_id=UserId(_UserID),
            username="john_doe",
            password=password_hasher.encode("password"),
            email="john_doe@example.com",
            uow=uow,
        )
    )


async def test_login(anon: ApiClient) -> None:
    response = await anon.post(
        "/api/v1/auth/login/",
        json={
            "username": "john_doe",
            "password": "password",
        },
        expected_status=status_codes.HTTP_200_OK,
    )

    assert response["id"] == str(_UserID)


async def test_after_login_cookie_set(anon: ApiClient, session_factory: SessionFactory) -> None:
    response = await anon.post(
        "/api/v1/auth/login/",
        json={
            "username": "john_doe",
            "password": "password",
        },
        as_response=True,
    )

    db_session = await session_factory.get_latest_session()
    cookies = SimpleCookie("\r\n".join(response.headers.get_list("Set-Cookie")))

    assert db_session is not None
    assert response.cookies.get("session-id") == cookies["session-id"].value == str(db_session.get("session_id"))
    assert cookies["session-id"]["expires"] == db_session["expires_at"].strftime("%a, %d %b %Y %H:%M:%S GMT")
    assert cookies["session-id"]["secure"] is True
    assert cookies["session-id"]["path"] == "/"
    assert cookies["session-id"]["httponly"] is True
    assert cookies["session-id"]["samesite"] == "lax"


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
async def test_login_works_only_for_post_request(anon: ApiClient, method: str) -> None:
    await getattr(anon, method)(
        "/api/v1/auth/login/",
        json={
            "username": "john_doe",
            "password": "password",
            "email": "john_doe@example.com",
        },
        expected_status=status_codes.HTTP_405_METHOD_NOT_ALLOWED,
    )


async def test_cannot_login_with_not_existing_username(anon: ApiClient) -> None:
    response = await anon.post(
        "/api/v1/auth/login/",
        json={
            "username": "another_username",
            "password": "password",
        },
        expected_status=status_codes.HTTP_401_UNAUTHORIZED,
    )

    assert response["error"] == "Authentication failed"
    assert response["detail"] == "Invalid username or password"
    assert response["status_code"] == status_codes.HTTP_401_UNAUTHORIZED


async def test_cannot_login_with_not_valid_password(anon: ApiClient) -> None:
    response = await anon.post(
        "/api/v1/auth/login/",
        json={
            "username": "john_doe",
            "password": "another_password",
        },
        expected_status=status_codes.HTTP_401_UNAUTHORIZED,
    )

    assert response["error"] == "Authentication failed"
    assert response["detail"] == "Invalid username or password"
    assert response["status_code"] == status_codes.HTTP_401_UNAUTHORIZED
