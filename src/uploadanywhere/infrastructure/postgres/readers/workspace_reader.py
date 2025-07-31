from dataclasses import dataclass

from uploadanywhere.infrastructure.postgres.readers.base_query import BaseQuery
from uploadanywhere.infrastructure.postgres.readers.base_reader import BaseReader


@dataclass
class WorkspaceQuery(BaseQuery):
    name: str | None = None
    owner_id: int | None = None


class WorkspaceReader(BaseReader[WorkspaceQuery]):
    table_name = "workspaces"
    allowed_sort_columns = ["name"]
    fields = ["workspace_id", "name"]
    default_sort_field = "workspace_id"
