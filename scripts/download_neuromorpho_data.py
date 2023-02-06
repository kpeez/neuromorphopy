"""Script for getting the SWC files of a neuromorpho.org query."""
import argparse
from pathlib import Path

from neuromorphopy import NeuroMorpho
from neuromorphopy.utils import load_json_query


def config_args() -> argparse.Namespace:
    """Configure argument parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--query_filename",
        type=str,
        default="",
        help="Path to query file to search for neurons on neuromorpho.org.",
    )
    parser.add_argument(
        "-e",
        "--export_path",
        type=str,
        default="",
        help="Path to save exported data.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = config_args()
    query = load_json_query(args.query_filename)
    print("Running query...")
    nm = NeuroMorpho(query)
    print("Downloading data from neuromorpho.org...")
    nm.download_query_swc()
    print("Exporting data...")

    metadata_filename = f"{Path(args.query_filename).stem}_metadata.csv"
    swc_filename = f"{Path(args.query_filename).stem}_swc.pkl"
    nm.export_metadata(args.export_path, metadata_filename)
    nm.export_swc_data(args.export_path, swc_filename)
