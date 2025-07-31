from datetime import UTC, datetime
from http.cookies import SimpleCookie

import pytest
from freezegun import freeze_time
from litestar import status_codes
from uuid6 import UUID, uuid7

from tests.core.api_client.api_client import ApiClient
from tests.core.utils import Any
from tests.factories.sessions import SessionFactory
from tests.factories.users import UserFactory
from uploadanywhere.domain.entities.base import UoWRegistrator
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.identifiers import UserId


async def test_register(api: ApiClient, user_factory: UserFactory) -> None:
    response = await api.post(
        "/api/v1/auth/register/",
        json={
            "username": "john_doe",
            "password": "password",
            "email": "john_doe@example.com",
        },
    )

    assert response["id"] == Any(str)
    assert await user_factory.fetch_user(response["id"]) == {
        "email": "john_doe@example.com",
        "password": Any(str),
        "user_id": UUID(response["id"]),
        "username": "john_doe",
    }


@freeze_time("2012-01-14 12:00:00")
async def test_after_register_cookie_set(anon: ApiClient, session_factory: SessionFactory) -> None:
    response = await anon.post(
        "/api/v1/auth/register/",
        json={
            "username": "john_doe",
            "password": "password",
            "email": "john_doe@example.com",
        },
        as_response=True,
    )

    db_session = await session_factory.get_latest_session()
    cookies = SimpleCookie("\r\n".join(response.headers.get_list("Set-Cookie")))

    assert db_session is not None
    assert response.cookies.get("session-id") == cookies["session-id"].value == str(db_session.get("session_id"))
    assert cookies["session-id"]["expires"] == db_session["expires_at"].strftime("%a, %d %b %Y %H:%M:%S GMT")
    assert cookies["session-id"]["expires"] == datetime(2012, 7, 12, 12, 0, 0, tzinfo=UTC).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    assert cookies["session-id"]["secure"] is True
    assert cookies["session-id"]["path"] == "/"
    assert cookies["session-id"]["httponly"] is True
    assert cookies["session-id"]["samesite"] == "lax"


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
async def test_register_works_only_for_post_request(anon: ApiClient, method: str) -> None:
    await getattr(anon, method)(
        "/api/v1/auth/register/",
        json={
            "username": "john_doe",
            "password": "password",
            "email": "john_doe@example.com",
        },
        expected_status=status_codes.HTTP_405_METHOD_NOT_ALLOWED,
    )


async def test_cannot_register_with_existing_username(
    api: ApiClient, user_factory: UserFactory, fake_uow_registrator: UoWRegistrator
) -> None:
    await user_factory.create_user(
        User(
            username="john_doe",
            email="john_doe@example.com",
            password="password",
            uow=fake_uow_registrator,
            user_id=UserId(uuid7()),
        )
    )

    response = await api.post(
        "/api/v1/auth/register/",
        json={
            "username": "john_doe",
            "password": "new_password",
            "email": "another_email@example.com",
        },
        expected_status=status_codes.HTTP_409_CONFLICT,
    )

    assert response["error"] == "User already exists"
    assert response["detail"] == "User with the same username already exists"
    assert response["status_code"] == status_codes.HTTP_409_CONFLICT


async def test_cannot_register_with_existing_email(
    api: ApiClient, user_factory: UserFactory, fake_uow_registrator: UoWRegistrator
) -> None:
    await user_factory.create_user(
        User(
            username="john_doe",
            email="john_doe@example.com",
            password="password",
            uow=fake_uow_registrator,
            user_id=UserId(uuid7()),
        )
    )

    response = await api.post(
        "/api/v1/auth/register/",
        json={
            "username": "another_username",
            "password": "new_password",
            "email": "john_doe@example.com",
        },
        expected_status=status_codes.HTTP_409_CONFLICT,
    )

    assert response["error"] == "User already exists"
    assert response["detail"] == "User with the same email already exists"
    assert response["status_code"] == status_codes.HTTP_409_CONFLICT
