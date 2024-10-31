from dataclasses import dataclass


@dataclass
class QueryFilter:
    field: str
    values: list[str]
    operator: str = "eq"  # eq, ne, gt, lt, etc.


class QueryBuilder:
    def __init__(self) -> None:
        self.filters: dict[str, list[str]] = {}
        self.sort_by: str | None = None
        self.sort_order: str = "asc"

    def filter(self, field: str, values: str | list[str], operator: str = "eq") -> "QueryBuilder":
        if isinstance(values, str):
            values = [values]
        self.filters[field] = values
        return self

    def sort(self, field: str, ascending: bool = True) -> "QueryBuilder":
        self.sort_by = field
        self.sort_order = "asc" if ascending else "desc"
        return self

    def build(self) -> dict[str, list[str]]:
        query = {}

        # Combine filters
        for field, values in self.filters.items():
            query[field] = values

        # Add sorting
        if self.sort_by:
            query["_sort"] = {"field": self.sort_by, "order": self.sort_order}

        return query
