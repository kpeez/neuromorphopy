"""Work with NeuroMorpho API."""
from __future__ import annotations
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from neuromorphopy.swc import download_swc_data, get_neuron_swc
from neuromorphopy.utils import check_api_status, request_url_get, request_url_post, NEUROMORPHO_API


MAX_NEURONS = 500


def get_query_fields() -> set[str]:
    """Get list of accepted search fields."""
    return set(request_url_get(f"{NEUROMORPHO_API}/neuron/fields").json()["Neuron Fields"])


def get_query_values(field: str) -> set[str]:
    """Get list of accepted values for a given search field."""
    return set(request_url_get(f"{NEUROMORPHO_API}/neuron/fields/{field}").json()["fields"])


def validate_search(query: dict[str, list[str]]) -> None:
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
    """
    Access NeuroMorpho API to get neuron reconstructions.

    Attributes:
        valid_field_names (set): Set containing the valid field names to use for a query.
        neuron_metadata(pd.DataFrame): Results of search query.
        swc_data (dict): dict of neuron_name and its swc data


    """

    def __init__(self) -> None:
        if check_api_status():
            self.valid_field_names: set[str] = get_query_fields()
            self.neuron_metadata: pd.DataFrame = pd.DataFrame()
            self.swc_data: dict[str, pd.DataFrame] = {}

        else:
            raise ConnectionError("The NeuroMorpho API is currently down.")

    def get_field_values(self, field: str) -> set[str]:
        """
        Get all possible values for a given field.

        Args:
            field (str): field name

        Returns:
            set[str]: Valid field values to use for search queries.
        """
        return get_query_values(field)

    def get_neuron_metadata(self, query: dict[str, list[str]]) -> None:
        """
        Get list of neurons from a search query.

        See list of query keys here: https://neuromorpho.org/api/neuron/fields

        Args:
            query (dict[str, str]): query values to filter neurons
        """
        validate_search(query)
        print("Beginning search...")
        # use an initial request to get query info
        total_neurons = request_url_post(query).json()["page"]["totalElements"]
        num_pages = np.ceil(total_neurons / MAX_NEURONS).astype(int)

        neuron_list = []
        for page_idx in range(num_pages):
            neuron_count = MAX_NEURONS
            page = request_url_post(query, params={"size": neuron_count, "page": page_idx})
            neuron_list.extend(page.json()["_embedded"]["neuronResources"])

        self._neuron_list = neuron_list
        self.neuron_metadata = pd.DataFrame(neuron_list)

    @staticmethod
    def neuron_swc_data(neuron_name: str) -> pd.DataFrame:
        """Get DataFrame of swc data for neuron using neuron_name."""
        return get_neuron_swc(neuron_name)

    def download_query_swc(self) -> None:
        """Look up neuron name and retrieve swc data from NeuroMorpho."""
        assert self.neuron_metadata.empty is False, "No metadata!"

        print(f"Downloading swc data for {len(self.neuron_metadata['neuron_name'])} neurons...")

        self.swc_data = download_swc_data(self.neuron_metadata["neuron_name"])

    def export_metadata(self, export_path: str, query_filename: str) -> None:
        """
        Export metadata as csv.

        Args:
            export_path (str): export path
            query_filename (str): name of metadata file
        """
        self.neuron_metadata.to_csv(f"{Path(export_path)}/{query_filename}.csv", index=False)

    def export_swc_data(self, export_path: str, swc_filename: str) -> None:
        """
        Export dict of swc data to pkl file.

        Args:
            export_path (str): export path
            swc_filename (str): name of pkl file
        """
        with open(f"{Path(export_path)}/{swc_filename}.pkl", "wb") as f:
            pickle.dump(self.swc_data, f, protocol=-1)
