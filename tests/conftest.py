import pytest


@pytest.fixture
def sample_query_dict():
    return {
        "filters": {
            "species": ["mouse", "rat"],
            "brain_region": ["neocortex"],
        },
        "sort": {"field": "brain_region", "order": "ascending"},
    }


@pytest.fixture
def sample_swc_content():
    return """# n T x y z R P
1 1 0.0 0.0 0.0 1.0 -1
2 3 1.0 1.0 1.0 0.5 1
3 3 2.0 2.0 2.0 0.5 2
"""


@pytest.fixture(autouse=True)
def mock_api_fields(mocker):
    """Mock the NeuroMorpho API fields endpoint to prevent network calls during tests."""
    mock_get = mocker.patch("neuromorphopy.query.request_url_get")

    def side_effect(url, **kwargs):
        mock_response = mocker.Mock()
        mock_response.is_success = True  # for httpx check
        if url.endswith("/neuron/fields"):
            mock_response.json.return_value = {
                "Neuron Fields": ["species", "brain_region", "cell_type"]
            }
        elif "/neuron/fields/" in url:
            field = url.split("/")[-1]
            values = {
                "species": ["mouse", "rat", "human"],
                "brain_region": ["neocortex", "hippocampus"],
                "cell_type": ["pyramidal"],
            }
            mock_response.json.return_value = {"fields": values.get(field, [])}
        return mock_response

    mock_get.side_effect = side_effect
    return mock_get
