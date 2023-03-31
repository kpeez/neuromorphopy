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
        "--query_file",
        type=str,
        help="Path to query file to search for neurons on NeuroMorpho.",
    )
    parser.add_argument(
        "-e",
        "--export_path",
        type=str,
        help="Path to export metadata and swc files to.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = config_args()
    print("Running query...")
    query = load_json_query(args.query_file)
    nm = NeuroMorpho(query)

    metadata_filename = f"{Path(args.query_file).stem}_metadata.csv"
    nm.export_metadata(args.export_path, metadata_filename)
    print("Finished downloading metadata.")
    nm.download_query_swc(args.export_path)

    print(f"Finished downloading data from {args.query_file}.")
