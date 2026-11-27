import textwrap
from unittest.mock import AsyncMock

import pytest
from asyncpg import Connection

from uploadanywhere.infrastructure.exceptions import InvalidSortingColumnError, InvalidSortingDirectionError
from uploadanywhere.infrastructure.postgres.readers.base_query import BaseQuery
from uploadanywhere.infrastructure.postgres.readers.base_reader import BaseReader


class MockQuery(BaseQuery):
    sort_by = "-id"

    def build_filters(self) -> tuple[str, list]:
        return "WHERE id > $1", [1]

    def get_pagination(self) -> tuple[int, int]:
        return 0, 1


class TestReader(BaseReader):
    table_name = "test_table"


@pytest.fixture
def mock_connection() -> AsyncMock:
    return AsyncMock(spec=Connection)


@pytest.fixture
def mock_query() -> MockQuery:
    return MockQuery()


async def test_fetch_many_raises_value_error_when_table_name_not_defined(mock_connection: Connection) -> None:
    reader: BaseReader[BaseQuery] = BaseReader(connection=mock_connection)

    with pytest.raises(ValueError, match="table_name must be defined in a subclass"):
        await reader.fetch_many(query=AsyncMock())


async def test_validate_sorting_raises_invalid_sorting_column_error(
    mock_connection: Connection, mock_query: MockQuery
) -> None:
    reader = TestReader(connection=mock_connection)
    mock_query.sort_by = "invalid_column"

    with pytest.raises(InvalidSortingColumnError, match="Invalid column for sorting: invalid_column"):
        await reader.fetch_many(query=mock_query)


def test_validate_sorting_raises_invalid_sorting_direction_error(mock_connection: Connection) -> None:
    reader = TestReader(connection=mock_connection)
    invalid_sort_by = "id"  # No '-' prefix, should default to 'ASC', which is valid

    # Temporarily change allowed_order_directions to make 'ASC' invalid
    reader.allowed_order_directions = ["DESC"]

    with pytest.raises(InvalidSortingDirectionError, match="Invalid sorting direction: ASC"):
        reader.validate_sorting(invalid_sort_by)


def test_validate_sorting_defaults_to_default_sort_field(mock_connection: Connection) -> None:
    reader = TestReader(connection=mock_connection)

    order_by, order_direction = reader.validate_sorting(None)

    assert order_by == "id"
    assert order_direction == "DESC"


def test_validate_sorting_parses_leading_dash_as_descending(mock_connection: Connection) -> None:
    reader = TestReader(connection=mock_connection)
    sort_by = "-id"

    order_by, order_direction = reader.validate_sorting(sort_by)

    assert order_by == "id"
    assert order_direction == "DESC"


def test_validate_sorting_parses_sort_by_without_dash_as_ascending(mock_connection: Connection) -> None:
    reader = TestReader(connection=mock_connection)
    order_by, order_direction = reader.validate_sorting("id")

    assert order_by == "id"
    assert order_direction == "ASC"


async def test_fetch_many_constructs_sql_with_correct_order_by_and_limit(
    mock_connection: Connection,
    mock_query: MockQuery,
) -> None:
    class TestReaderWithAnotherFields(BaseReader):
        table_name = "test_table"
        fields = ["id", "name"]

    mock_connection.fetchval = AsyncMock()  # type: ignore[method-assign]

    reader = TestReaderWithAnotherFields(connection=mock_connection)

    await reader.fetch_many(query=mock_query)

    expected_sql = """
    WITH total_count AS (
        SELECT COUNT(*) as cnt FROM test_table WHERE id > $1
    )
    SELECT json_build_object(
        'result', COALESCE(json_agg(data), '[]'::json),
        'count', (SELECT cnt FROM total_count),
        'next', CASE
            WHEN (0 + 10) < (SELECT cnt FROM total_count)
            THEN 1 + 1
            ELSE NULL
        END,
        'previous', CASE
            WHEN 1 > 1
            THEN 1 - 1
            ELSE NULL
        END
    )
    FROM (
        SELECT id, name FROM test_table
        WHERE id > $1
        ORDER BY id DESC
        LIMIT 10
        OFFSET 0
    ) as data;
    """
    mock_connection.fetchval.assert_awaited_once_with(textwrap.dedent(expected_sql).strip(), 1)
