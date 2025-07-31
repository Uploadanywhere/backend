import textwrap

from asyncpg import Connection

from uploadanywhere.infrastructure.exceptions import InvalidSortingColumnError, InvalidSortingDirectionError
from uploadanywhere.infrastructure.postgres.readers.base_query import BaseQuery


class BaseReader[Q: BaseQuery]:
    table_name: str | None = None
    allowed_sort_columns: list[str] = ["id"]
    allowed_order_directions: list[str] = ["ASC", "DESC"]
    fields: list[str] = ["*"]
    default_sort_field: str = "-id"

    def __init__(self, connection: Connection) -> None:
        self._con = connection

    def validate_sorting(self, sort_by: str | None) -> tuple[str, str]:
        if not sort_by:
            sort_by = self.default_sort_field
        if sort_by.startswith("-"):
            order_by = sort_by[1:]
            order_direction = "DESC"
        else:
            order_by = sort_by
            order_direction = "ASC"

        if order_by not in self.allowed_sort_columns:
            raise InvalidSortingColumnError(f"Invalid column for sorting: {order_by}")
        if order_direction not in self.allowed_order_directions:
            raise InvalidSortingDirectionError(f"Invalid sorting direction: {order_direction}")
        return order_by, order_direction

    async def fetch_many(self, query: Q) -> dict:
        if not self.table_name:
            raise ValueError("table_name must be defined in a subclass")

        where_clause, values = query.build_filters()

        sort_by = query.sort_by
        order_by, order_direction = self.validate_sorting(sort_by)

        offset, page = query.get_pagination()

        selected_fields = ", ".join(self.fields)

        sql = f"""
        WITH total_count AS (
            SELECT COUNT(*) as cnt FROM {self.table_name} {where_clause}
        )
        SELECT json_build_object(
            'result', COALESCE(json_agg(data), '[]'::json),
            'count', (SELECT cnt FROM total_count),
            'next', CASE
                WHEN ({offset} + {query.limit}) < (SELECT cnt FROM total_count)
                THEN {page} + 1
                ELSE NULL
            END,
            'previous', CASE
                WHEN {page} > 1
                THEN {page} - 1
                ELSE NULL
            END
        )
        FROM (
            SELECT {selected_fields} FROM {self.table_name}
            {where_clause}
            ORDER BY {order_by} {order_direction}
            LIMIT {query.limit}
            OFFSET {offset}
        ) as data;
        """  # noqa: S608  # I KNOW, here can be SQL injections, but I think it's safe here, i wrote test cases for it
        sql = textwrap.dedent(sql).strip()

        return await self._con.fetchval(sql, *values)
