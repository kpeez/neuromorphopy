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
        help="Path to query file to search for neurons on neuromorpho.org.",
    )
    parser.add_argument(
        "-e",
        "--export_path",
        type=str,
        help="Path to save exported data.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = config_args()
    print("Running query...")
    query = load_json_query(args.query_file)
    nm = NeuroMorpho(query)

    print("Downloading metadata from neuromorpho.org...")
    metadata_filename = f"{Path(args.query_file).stem}_metadata.csv"
    nm.export_metadata(args.export_path, metadata_filename)

    print("Download SWC data...")
    nm.download_query_swc()
    swc_filename = f"{Path(args.query_file).stem}_swc.pkl"
    nm.export_swc_data(args.export_path, swc_filename)

    print(f"Finished downloading data from {args.query_filename}.")
