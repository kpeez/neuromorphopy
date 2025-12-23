import json

import pytest
import typer
import yaml

from neuromorphopy.cli import validate
from neuromorphopy.query import Query


def test_query_from_yaml_file(tmp_path, sample_query_dict):
    query_file = tmp_path / "query.yaml"
    with open(query_file, "w") as f:
        yaml.dump(sample_query_dict, f)

    query = Query.from_file(query_file)

    # Expected output matches the input filters + the special _sort key
    expected = sample_query_dict["filters"].copy()
    expected["_sort"] = {
        "field": sample_query_dict["sort"]["field"],
        "order": "asc",  # QuerySort logic converts boolean/string to "asc"/"desc"
    }

    assert query == expected


def test_query_from_json_file(tmp_path, sample_query_dict):
    query_file = tmp_path / "query.json"
    with open(query_file, "w") as f:
        json.dump(sample_query_dict, f)

    query = Query.from_file(query_file)
    assert isinstance(query, dict)
    assert "species" in query
    assert "_sort" in query


def test_validate_missing_filters(tmp_path):
    query_file = tmp_path / "bad_query.yaml"
    with open(query_file, "w") as f:
        yaml.dump({"sort": {}}, f)

    with pytest.raises(typer.Exit):
        validate(query_file, quiet=True)


def test_validate_invalid_sort_field(tmp_path):
    query_file = tmp_path / "bad_sort.yaml"
    with open(query_file, "w") as f:
        yaml.dump(
            {"filters": {"species": ["mouse"]}, "sort": {"field": "INVALID_FIELD", "order": "asc"}},
            f,
        )

    # validate() catches ValueError and raises typer.Exit
    with pytest.raises(typer.Exit):
        validate(query_file, quiet=True)
