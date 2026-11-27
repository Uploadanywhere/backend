import pytest

from tests.factories.sessions import SessionFactory
from tests.factories.users import UserFactory
from tests.factories.workspaces import WorkspaceFactory
from uploadanywhere.domain.entities.session import Session
from uploadanywhere.domain.entities.user import User
from uploadanywhere.domain.entities.workspace import Workspace


@pytest.fixture
async def db_user(user_factory: UserFactory, user: User) -> User:
    await user_factory.create_user(user)
    return user


@pytest.fixture
async def db_session(
    session_factory: SessionFactory,
    session: Session,
    db_user: User,  # This need for correct session creation  # ruff: ignore[unused-function-argument]
) -> Session:
    await session_factory.create_session(session)
    return session


@pytest.fixture
async def db_workspace(workspace_factory: WorkspaceFactory, workspace: Workspace) -> Workspace:
    await workspace_factory.create_workspace(workspace)
    return workspace
