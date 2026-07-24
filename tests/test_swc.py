import datetime

import pandas as pd
import pytest

from neuromorphopy.io.swc import (
    download_neuron_data,
    download_swc_data,
    get_neuron_swc,
    validate_swc_data,
)


def test_get_neuron_swc_parsing(mocker, sample_swc_content):
    # Mock the request to return sample content
    mock_resp = mocker.Mock()
    mock_resp.text = sample_swc_content
    mock_resp.is_success = True
    mocker.patch("neuromorphopy.io.swc.request_url_get", return_value=mock_resp)
    # Mock get_swc_url to return a dummy URL
    mocker.patch("neuromorphopy.io.swc.get_swc_url", return_value="http://fake.url")

    df = get_neuron_swc("test_neuron")

    assert len(df) == 3
    assert list(df.columns) == ["n", "type", "x", "y", "z", "radius", "parent"]
    assert df["type"].dtype == int
    assert df["x"].dtype == float


def test_validate_swc_data_no_root():
    df = pd.DataFrame(
        {
            "n": [1, 2],
            "type": [1, 3],
            "parent": [2, 1],  # Loop, no root (-1)
        }
    )

    with pytest.raises(ValueError, match="does not contain a root node"):
        validate_swc_data(df)


def test_validate_swc_data_fix_soma():
    # Root exists but type is not 1 (soma)
    df = pd.DataFrame({"n": [1], "type": [3], "parent": [-1]})

    validate_swc_data(df)
    assert df.loc[0, "type"] == 1


def test_download_neuron_data_writes_file(mocker, tmp_path):
    # Mock get_neuron_swc to return a simple DF
    df = pd.DataFrame(
        {"n": [1], "type": [1], "x": [0], "y": [0], "z": [0], "radius": [1], "parent": [-1]}
    )
    mocker.patch("neuromorphopy.io.swc.get_neuron_swc", return_value=df)

    result = download_neuron_data("test_neuron", tmp_path)

    assert "Downloaded test_neuron" in result
    expected_file = tmp_path / "test_neuron.swc"
    assert expected_file.exists()
    content = expected_file.read_text()
    assert "# n type" in content  # Header check


def test_download_swc_data_skips_existing(mocker, tmp_path):
    # Setup: Create an existing file
    dirname = datetime.datetime.now().astimezone().strftime("%Y_%m_%d_%H_%M-swc_files")
    download_dir = tmp_path / dirname
    download_dir.mkdir(parents=True)
    (download_dir / "existing.swc").touch()

    # Mock download_neuron_data
    mock_download = mocker.patch("neuromorphopy.io.swc.download_neuron_data")

    # Run with a list including the existing one
    download_swc_data(["existing", "new"], download_dir=tmp_path)

    # Ensure only "new" was attempted
    # Note: download_swc_data uses thread pool, so order isn't guaranteed,
    # but "existing" should be filtered out before the pool.
    mock_download.assert_called_once()
    args = mock_download.call_args[0]
    assert args[0] == "new"
