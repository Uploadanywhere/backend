import typing as t
from unittest.mock import AsyncMock, MagicMock

import pytest

from uploadanywhere.application.command_processors.transaction_processor import TransactionProcessor
from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.uow import AsyncUoW, UoWCommitter


class MockCommand:
    pass


class MockUoW(UoWCommitter):
    def __init__(self) -> None:
        pass

    commit = AsyncMock()


@pytest.fixture
def mock_processor() -> MagicMock:
    return MagicMock(spec=CommandProcessor)


@pytest.fixture
def uow_mock() -> MockUoW:
    return MockUoW()


async def test_transaction_processor(uow_mock: AsyncUoW, mock_processor: MagicMock) -> None:
    processor = TransactionProcessor(uow_mock, t.cast(CommandProcessor, mock_processor))
    command = MockCommand()

    await processor.process(command)

    mock_processor.process.assert_awaited_once_with(command)
