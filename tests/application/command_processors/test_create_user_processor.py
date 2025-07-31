import pytest
from dishka import AsyncContainer
from uuid6 import UUID

from tests.core.utils import Any
from tests.factories.users import UserFactory
from uploadanywhere.application.command_processors.create_user_processor import CreateUserCommand, CreateUserProcessor
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.id_generator import IDGenerator
from uploadanywhere.application.interfaces.password_hasher import PasswordHasher
from uploadanywhere.application.interfaces.uow import AsyncUoW
from uploadanywhere.domain.exceptions import AlreadyExistsError, ValidationError
from uploadanywhere.domain.identifiers import UserId
from uploadanywhere.domain.interfaces.user_repository import UserRepository
from uploadanywhere.domain.services import UserCreator


@pytest.fixture
async def uow(rs_container: AsyncContainer) -> AsyncUoW:
    return await rs_container.get(AsyncUoW)


@pytest.fixture
async def user_creator(rs_container: AsyncContainer, uow: AsyncUoW) -> UserCreator:
    user_repository = await rs_container.get(UserRepository)
    return UserCreator(user_repository, uow)


@pytest.fixture
async def processor(container: AsyncContainer, user_creator: UserCreator) -> CreateUserProcessor:
    id_gen = await container.get(IDGenerator[UUID])
    password_hasher = await container.get(PasswordHasher)
    return CreateUserProcessor(id_generator=id_gen, password_hasher=password_hasher, create_user=user_creator)


async def test_create_user_processor(uow: AsyncUoW, processor: CreateUserProcessor, user_factory: UserFactory) -> None:
    command = CreateUserCommand("john_doe", "john_doe@example.com", "password")

    result = await processor.process(command)
    await uow.commit()  # save changes to the database

    db_user = await user_factory.fetch_user(result)
    assert result == Any(UUID)
    assert db_user == {
        "email": "john_doe@example.com",
        "password": Any(str),
        "user_id": result,
        "username": "john_doe",
    }
    assert db_user["password"] != "password"  # noqa: S105


async def test_create_user_processor_generate_unique_id(processor: CreateUserProcessor) -> None:
    command = CreateUserCommand("john_doe", "john_doe@example.com", "password")

    result = await processor.process(command)
    result2 = await processor.process(command)

    assert result != result2


async def test_processor_raises_exception_for_empty_email(processor: CreateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Email cannot be empty"):
        await processor.process(CreateUserCommand("john_doe", "", "password"))


async def test_processor_raises_exception_for_empty_password(processor: CreateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Password cannot be empty"):
        await processor.process(CreateUserCommand("john_doe", "john_doe@example.com", ""))


async def test_processor_raises_exception_for_none_username(processor: CreateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        await processor.process(CreateUserCommand(None, "john_doe@example.com", "password"))  # type: ignore[arg-type]


async def test_processor_raises_exception_for_none_password(processor: CreateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Password cannot be empty"):
        await processor.process(CreateUserCommand("john_doe", "john_doe@example.com", None))  # type: ignore[arg-type]


async def test_processor_raises_exception_for_none_email(processor: CreateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Email cannot be empty"):
        await processor.process(CreateUserCommand("john_doe", None, "password"))  # type: ignore[arg-type]


async def test_processor_raises_exception_for_empty_username(processor: CreateUserProcessor) -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        await processor.process(CreateUserCommand("", "john_doe@example.com", "password"))


async def test_processor_with_transaction_processor_in_chain(
    rs_container: AsyncContainer, user_factory: UserFactory
) -> None:
    create_user = await rs_container.get(CommandProcessor[CreateUserCommand, UserId])

    result = await create_user.process(CreateUserCommand("john_doe", "john_doe@example.com", "password"))

    db_user = await user_factory.fetch_user(result)
    assert result == Any(UUID)
    assert db_user == {
        "email": "john_doe@example.com",
        "password": Any(str),
        "user_id": result,
        "username": "john_doe",
    }
    assert db_user["password"] != "password"  # noqa: S105


async def test_processor_raises_exception_for_exists_email(rs_container: AsyncContainer) -> None:
    create_user = await rs_container.get(CommandProcessor[CreateUserCommand, UserId])

    await create_user.process(CreateUserCommand("john_doe", "john_doe@example.com", "password"))

    # Act & Assert
    with pytest.raises(AlreadyExistsError, match="User with the same email already exists"):
        await create_user.process(CreateUserCommand("Username2", "john_doe@example.com", "password"))


async def test_processor_raises_exception_for_exists_username(rs_container: AsyncContainer) -> None:
    create_user = await rs_container.get(CommandProcessor[CreateUserCommand, UserId])

    await create_user.process(CreateUserCommand("Username", "john_doe@example.com", "password"))

    # Act & Assert
    with pytest.raises(AlreadyExistsError, match="User with the same username already exists"):
        await create_user.process(CreateUserCommand("Username", "another@example.com", "password"))
