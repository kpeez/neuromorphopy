"""Work with NeuroMorpho API."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from IPython.display import Image
from tqdm import tqdm

from neuromorphopy.swc import download_swc_data, get_neuron_swc
from neuromorphopy.utils import (
    NEUROMORPHO_API,
    check_api_status,
    clean_metadata_columns,
    get_image_url,
    request_url_get,
    request_url_post,
)

MAX_NEURONS = 500


def get_query_fields() -> set[str]:
    """Get list of accepted search fields."""
    return set(request_url_get(f"{NEUROMORPHO_API}/neuron/fields").json()["Neuron Fields"])


def get_query_values(field: str) -> set[str]:
    """Get list of accepted values for a given search field."""
    return set(request_url_get(f"{NEUROMORPHO_API}/neuron/fields/{field}").json()["fields"])


def validate_query(query: dict[str, list[str]]) -> None:
    """Validate search query to ensure field and its items are acceptable."""
    query_fields = get_query_fields()
    print("Validating search query...")
    if not set(query.keys()).issubset(query_fields):
        raise ValueError(f"Invalid search field: {set(query.keys()) - query_fields}")

    for field, values in query.items():
        query_values = get_query_values(field)
        if not set(values).issubset(query_values):
            raise ValueError(f"Invalid field values for {field}: {set(values) - query_values}")


class NeuroMorpho:
    """Access NeuroMorpho API to get neuron reconstructions.

    Attributes:
        valid_field_names (set): Set containing the valid field names to use for a query.
        neuron_metadata(pd.DataFrame): Results of search query.
    """

    def __init__(self, query: dict[str, list[str]] | None = None) -> None:
        if check_api_status():
            self.valid_field_names: set[str] = get_query_fields()
            self.neuron_metadata: pd.DataFrame = pd.DataFrame()
            self.query = query
            if self.query:
                self.search_archives()
        else:
            raise ConnectionError("The NeuroMorpho API is currently down.")

    def get_field_values(self, field: str) -> set[str]:
        """Get all possible values for a given field.

        Args:
            field (str): field name

        Returns:
            set[str]: Valid field values to use for search queries.
        """
        return get_query_values(field)

    @staticmethod
    def get_neuron_metadata(query: dict[str, list[str]]) -> pd.DataFrame:
        """Get list of neurons from a search query.

        See list of query keys here: https://neuromorpho.org/api/neuron/fields

        Args:
            query (dict[str, str]): query values to filter neurons
        """
        validate_query(query)
        # use an initial request to get query info
        total_neurons = request_url_post(query).json()["page"]["totalElements"]
        num_pages = np.ceil(total_neurons / MAX_NEURONS).astype(int)
        print(f"Downloading metadata for {total_neurons} neurons.")

        neuron_list = []  # list of neuron metadata dicts
        for page_idx in tqdm(
            range(num_pages),
            unit="page",
            desc="Processing pages",
            bar_format="{desc}[{n_fmt}/{total_fmt}]{percentage:3.0f}%|{bar}"
            "{postfix} [{elapsed}<{remaining}]",
        ):
            neuron_count = MAX_NEURONS
            page = request_url_post(query, params={"size": neuron_count, "page": page_idx})
            neuron_list.extend(page.json()["_embedded"]["neuronResources"])

        metadata = pd.DataFrame(neuron_list)

        return clean_metadata_columns(metadata)

    def search_archives(self) -> None:
        """Search NeuroMorpho archives."""
        if not self.query:
            raise ValueError("No query provided.")

        self.neuron_metadata = self.get_neuron_metadata(self.query)

    @staticmethod
    def neuron_swc_data(neuron_name: str) -> pd.DataFrame:
        """Get DataFrame of swc data for neuron using neuron_name."""
        return get_neuron_swc(neuron_name)

    def download_query_swc(self, download_dir: str | Path | None = None) -> None:
        """Download swc data from NeuroMorpho for all neurons in metadata.

        This function will create a directory in the ``download_dir`` (or current working directory
        if no directory is provided). All neurons in the ``neuron_list`` will be saved here.

        Args:
            neuron_list (list[str] | pd.Series[str]): List of neuron names to retrieve swc data for.
            download_dir (str | Path): Path to download swc data to. If None, will download to
            current working directory.
        """
        assert self.neuron_metadata.empty is False, "No metadata!"

        if self.neuron_metadata.empty:
            print("No metadata! -- Downloading metadata...")
            self.get_neuron_metadata()

        download_swc_data(self.neuron_metadata["neuron_name"], download_dir=download_dir)

    def export_metadata(self, export_path: str, query_filename: str) -> None:
        """Export metadata as csv.

        Args:
            export_path (str): export path
            query_filename (str): name of metadata file
        """
        export_filename = (
            f"{query_filename}.csv" if Path(query_filename).suffix != ".csv" else query_filename
        )

        self.neuron_metadata.to_csv(f"{Path(export_path)}/{export_filename}", index=False)

    @staticmethod
    def view_neuron_image(neuron_name: str) -> Image:
        """View neuron image using neuron name."""
        get_image_url(neuron_name)

        return Image(url=f"https://neuromorpho.org/neuron_info.jsp?neuron_name={neuron_name}")
