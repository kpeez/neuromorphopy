from pathlib import Path

import pandas as pd
import pytest

from neuromorphopy.utils.api_utils import (
    clean_metadata_columns,
    generate_grouped_path,
    request_url_get,
    request_url_post,
)


def test_clean_metadata_columns():
    df = pd.DataFrame(
        {
            "neuron_name": ["Neuron1"],
            "brain_region": ["['neocortex']"],
            "cell_type": ["layer 5 pyramidal cell"],
            "species": ["Mouse Rat"],
        }
    )

    cleaned = clean_metadata_columns(df)

    assert cleaned["brain_region"].iloc[0] == "neocortex"  # strip []
    assert cleaned["cell_type"].iloc[0] == "5_pyramidal_cell"  # replace "layer "
    assert cleaned["species"].iloc[0] == "mouse_rat"  # lower, replace " " with "_"


def test_generate_grouped_path():
    base = Path("/data")
    neuron = {"species": "mouse", "archive": "Allen/Institute"}

    # Simple group
    path = generate_grouped_path(base, neuron, "species")
    assert path == base / "mouse"

    # Sanitization
    path = generate_grouped_path(base, neuron, "archive")
    assert path == base / "Allen_Institute"

    # Multiple levels
    path = generate_grouped_path(base, neuron, "species,archive")
    assert path == base / "mouse" / "Allen_Institute"


def test_request_url_get_error(mocker):
    mock_client = mocker.patch("neuromorphopy.utils.api_utils.client")
    mock_response = mocker.Mock()
    mock_response.is_success = False
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_client.get.return_value = mock_response

    with pytest.raises(ValueError, match="Request failed: 404"):
        request_url_get("http://test.com")


def test_request_url_post_error(mocker):
    mock_client = mocker.patch("neuromorphopy.utils.api_utils.client")
    mock_response = mocker.Mock()
    mock_response.is_success = False
    mock_response.status_code = 500
    mock_response.text = "Server Error"
    mock_client.post.return_value = mock_response

    with pytest.raises(ValueError, match="Request failed: 500"):
        request_url_post({"q": ["val"]})
