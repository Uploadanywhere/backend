from unittest.mock import AsyncMock

import pytest
from litestar import Litestar

from uploadanywhere.main.rest import lifespan


@pytest.fixture
def mock_app() -> Litestar:
    app = AsyncMock(spec=Litestar)
    app.state.dishka_container.close = AsyncMock()
    return app


async def test_lifespan_context_manager_with_mock_app(mock_app: Litestar) -> None:
    async with lifespan(mock_app):
        pass

    mock_app.state.dishka_container.close.assert_awaited_once()


async def test_lifespan_context_manager_closes_dishka_container(mock_app: Litestar) -> None:
    async with lifespan(mock_app):
        pass

    mock_app.state.dishka_container.close.assert_awaited_once()


async def test_lifespan_context_manager_handles_exceptions_gracefully(mock_app: Litestar) -> None:
    mock_app.state.dishka_container.close.side_effect = Exception("Test exception")

    with pytest.raises(Exception, match="Test exception"):
        async with lifespan(mock_app):
            pass

    mock_app.state.dishka_container.close.assert_awaited_once()


async def test_lifespan_context_manager_accesses_app_state(mock_app: Litestar) -> None:
    async with lifespan(mock_app):
        assert hasattr(mock_app.state, "dishka_container")


async def test_lifespan_context_manager_no_resource_leak(mock_app: Litestar) -> None:
    async with lifespan(mock_app):
        assert not mock_app.state.dishka_container.close.called

    mock_app.state.dishka_container.close.assert_awaited_once()


async def test_lifespan_context_manager_multiple_usage(mock_app: Litestar) -> None:
    async with lifespan(mock_app):
        pass

    async with lifespan(mock_app):
        pass

    assert mock_app.state.dishka_container.close.await_count == 2


async def test_lifespan_context_manager_does_not_alter_app_state_unexpectedly(mock_app: Litestar) -> None:
    original_state = mock_app.state.dishka_container

    async with lifespan(mock_app):
        pass

    assert mock_app.state.dishka_container == original_state


async def test_lifespan_context_manager_supports_async_operations(mock_app: Litestar) -> None:
    async def async_operation() -> str:  # ruff: ignore[unused-async]
        return "async operation completed"

    async with lifespan(mock_app):
        result = await async_operation()
        assert result == "async operation completed"

    mock_app.state.dishka_container.close.assert_awaited_once()
