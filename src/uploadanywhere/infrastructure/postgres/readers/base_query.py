from dataclasses import asdict, dataclass


@dataclass
class BaseQuery:
    limit: int = 10
    page: int = 1
    sort_by: str | None = None

    def build_filters(self) -> tuple[str, list]:
        filters = asdict(self)
        filters.pop("limit", None)
        filters.pop("page", None)
        filters.pop("sort_by", None)

        conditions = []
        values: list[str] = []
        operator_map = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}

        for key, value in filters.items():
            if value is None:
                continue

            for suffix, operator in operator_map.items():
                if key.endswith(f"_{suffix}"):
                    column = key.removesuffix(f"_{suffix}")
                    conditions.append(f"{column} {operator} ${len(values) + 1}")
                    values.append(value)
                    break
            else:
                if key == "name":
                    conditions.append(f"{key} ILIKE ${len(values) + 1}")
                    value = f"%{value}%"  # ruff: ignore[redefined-loop-name]
                else:
                    conditions.append(f"{key} = ${len(values) + 1}")
                values.append(value)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return where_clause, values

    def get_sorting(self, allowed_columns: list[str]) -> tuple[str, str]:
        if not self.sort_by:
            return "id", "ASC"

        order_direction = "ASC"
        column = self.sort_by

        if self.sort_by.startswith("-"):
            column = self.sort_by[1:]
            order_direction = "DESC"

        if column not in allowed_columns:
            return "id", "ASC"

        return column, order_direction

    def get_pagination(self) -> tuple[int, int]:
        page = max(self.page, 1)
        offset = (page - 1) * self.limit
        return offset, page
