import logging

from neuromorphopy import api
from neuromorphopy.utils import get_logger, setup_logging


def test_api_uses_package_logger_not_root():
    """api.py must log through the `neuromorphopy` logger so CLI flags apply to it."""
    assert api.logger is get_logger()
    assert api.logger is not logging.getLogger()


def test_file_logging_captures_api_messages(tmp_path):
    """Messages emitted from api.py land in the file configured by --log-to-file."""
    query_file = tmp_path / "query.yaml"
    query_file.write_text("filters: {}\n")

    setup_logging(verbose=True, log_to_file=True, output_dir=tmp_path, query_file=query_file)
    try:
        api.logger.info("marker-from-api")

        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) == 1
        assert "marker-from-api" in log_files[0].read_text()
    finally:
        get_logger().handlers.clear()
