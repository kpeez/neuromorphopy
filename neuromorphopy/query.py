import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .exceptions import ApiError, ValidationError
from .utils import NEUROMORPHO_API, request_url_get


class Query:
    """Build and validate NeuroMorpho queries."""

    def __init__(self) -> None:
        self._config = QueryConfig()

    @classmethod
    def from_file(cls, path: Path | str) -> dict[str, list[str]]:
        """Create and build query directly from JSON or YAML file."""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        if path.suffix.lower() in {".yml", ".yaml"}:
            data = yaml.safe_load(path.read_text())
        elif path.suffix.lower() == ".json":
            data = json.loads(path.read_text())
        else:
            raise ValueError("Config file must be JSON or YAML")

        config = QueryConfig.model_validate(data)
        builder = cls()
        builder._config = config
        return builder.build()

    def filter(self, field: str, values: str | list[str]) -> "Query":
        """Add a filter with validation."""
        if isinstance(values, str):
            values = [values]

        self._config.validate_field(field, values)
        filters = dict(self._config.filters)
        filters[field] = values
        self._config = QueryConfig(filters=filters, sort=self._config.sort)
        return self

    def sort(self, field: str, ascending: bool = True) -> "Query":
        """Add sorting with validation."""
        if field not in QueryFields.get_fields():
            raise ValueError(f"Invalid field: {field}")

        self._config = QueryConfig(
            filters=self._config.filters, sort=QuerySort(field=field, ascending=ascending)
        )
        return self

    def build(self) -> dict[str, list[str]]:
        """Build the final query dictionary."""
        query = dict(self._config.filters)
        if self._config.sort:
            query["_sort"] = {"field": self._config.sort.field, "order": self._config.sort.order}

        return query


class QueryFields:
    """Helper class for accessing NeuroMorpho query field information."""

    @classmethod
    @lru_cache(maxsize=1)
    def get_fields(cls) -> set[str]:
        """Get all valid query fields from NeuroMorpho API."""
        response = request_url_get(f"{NEUROMORPHO_API}/neuron/fields")
        return set(response.json()["Neuron Fields"])

    @classmethod
    @lru_cache(maxsize=100)
    def get_values(cls, field: str) -> set[str]:
        """Get valid values for a specific field."""
        if field not in cls.get_fields():
            raise ValidationError(f"Invalid field: {field}")

        try:
            response = request_url_get(f"{NEUROMORPHO_API}/neuron/fields/{field}")
            return set(response.json()["fields"])
        except Exception as err:
            raise ApiError(f"Failed to fetch values for field {field}: {err!s}") from err

    @classmethod
    def describe(cls) -> dict[str, set[str]]:
        """Get all fields and their valid values."""
        return {field: cls.get_values(field) for field in cls.get_fields()}


@dataclass
class QueryFilter:
    field: str
    values: list[str]


@dataclass
class QuerySort:
    field: str
    ascending: bool = True

    @property
    def order(self) -> str:
        return "asc" if self.ascending else "desc"


class QueryConfig(BaseModel):
    """Query configuration with validation."""

    filters: dict[str, list[str]] = Field(default_factory=dict)
    sort: QuerySort | None = None

    @classmethod
    @lru_cache(maxsize=1)
    def get_valid_fields(cls) -> set[str]:
        """Get all valid fields from NeuroMorpho API."""
        response = request_url_get(f"{NEUROMORPHO_API}/neuron/fields")
        return set(response.json()["Neuron Fields"])

    @classmethod
    @lru_cache(maxsize=100)
    def get_field_values(cls, field: str) -> set[str]:
        """Get valid values for a specific field."""
        response = request_url_get(f"{NEUROMORPHO_API}/neuron/fields/{field}")
        return set(response.json()["fields"])

    @staticmethod
    def validate_field(field: str, values: list[str]) -> None:
        """Validate a single field and its values."""
        if field not in QueryFields.get_fields():
            raise ValueError(f"Invalid field: {field}")

        valid_values = QueryFields.get_values(field)
        invalid_values = set(values) - valid_values
        if invalid_values:
            raise ValueError(
                f"Invalid values for {field}: {invalid_values}\n"
                f"Valid values are: {valid_values}"
            )
