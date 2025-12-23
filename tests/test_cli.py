import typer
import yaml
from typer.testing import CliRunner

from neuromorphopy.cli import app

runner = CliRunner()


def test_preview_invalid_query(tmp_path, mocker):
    query_file = tmp_path / "invalid.yaml"
    query_file.touch()

    # Mock validation failure
    mocker.patch("neuromorphopy.cli.validate", side_effect=typer.Exit(code=1))

    result = runner.invoke(app, ["preview", str(query_file)])
    assert result.exit_code == 1


def test_download_calls_search(tmp_path, mocker, sample_query_dict):
    query_file = tmp_path / "query.yaml"
    with open(query_file, "w") as f:
        yaml.dump(sample_query_dict, f)

    # Mock validate to pass
    mocker.patch("neuromorphopy.cli.validate", return_value=(True, None))
    # Mock Query.from_file to return sample dict
    mocker.patch("neuromorphopy.cli.Query.from_file", return_value={"species": ["mouse"]})
    # Mock setup_logging to avoid file IO
    mocker.patch("neuromorphopy.cli.setup_logging")
    mock_get_logger = mocker.patch("neuromorphopy.cli.get_logger")
    mock_logger = mock_get_logger.return_value

    # Mock search_and_download
    mock_search = mocker.patch("neuromorphopy.cli.search_and_download", return_value=10)

    result = runner.invoke(app, ["download", str(query_file)])

    assert result.exit_code == 0
    mock_search.assert_called_once()
    # Verify logger.info was called with completion message
    assert mock_logger.info.call_count >= 2
    mock_logger.info.assert_any_call("Download complete!")
