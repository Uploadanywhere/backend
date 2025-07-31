from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker
from uuid6 import uuid7

from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.entities.workspace import Workspace
from uploadanywhere.domain.identifiers import SessionId, UserId, WorkspaceId
from uploadanywhere.infrastructure.postgres.uow import UnitOfWork


@pytest.fixture
def user(uow: UnitOfWork, faker: Faker) -> User:
    return User(
        user_id=UserId(uuid7()),
        username=faker.user_name(),
        email=faker.email(),
        password=faker.password(),
        uow=uow,
    )


@pytest.fixture
def session(user: User, uow: UnitOfWork) -> Session:
    return Session(
        uow=uow,
        session_id=SessionId(uuid7()),
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )


@pytest.fixture
def workspace(user: User, uow: UnitOfWork, faker: Faker) -> Workspace:
    return Workspace(
        uow=uow,
        workspace_id=WorkspaceId(uuid7()),
        owner_id=user.id,
        name=faker.catch_phrase(),
    )
