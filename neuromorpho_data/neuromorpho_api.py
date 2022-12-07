"""Work with NeuroMorpho API."""
from __future__ import annotations

import contextlib
import io
import pickle
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util import ssl_

# globals
NEUROMORPHO = "https://neuromorpho.org"
NEUROMORPHO_API = "https://neuromorpho.org/api"
NEURON_INFO = f"{NEUROMORPHO}/neuron_info.jsp?neuron_name="
MAX_NEURONS = 500


def add_dh_cipher_set() -> None:
    """
    Update SSL cipher list to ignore DH KEY TOO SMALL error.

    See:
    https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small
    """
    disable_warnings(InsecureRequestWarning)
    ssl_.DEFAULT_CIPHERS += "HIGH:!DH:!aNULL"
    with contextlib.suppress(AttributeError):
        requests.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += (  # type:ignore
            "HIGH:!DH:!aNULL"
        )


def _check_response_validity(page: requests.models.Response) -> None:
    """Ensure we have a valid response."""
    bad_status = {
        400: "400 error: Bad request, usually wrong parameters to select queries.",
        404: "404 error: Resource not found or does not exist.",
        405: "405 error: Unsupported HTTP method used.",
        500: "500 error: Internal Server Error. Please notify nmoadmin@gmu.edu.",
    }

    if page.status_code == 200:
        return

    else:
        raise ValueError(bad_status[page.status_code])


def check_api_status() -> bool:
    """
    Check status of API health.

    Returns:
        bool: True if API is working, False if not.
    """
    api_health = request_url_get(f"{NEUROMORPHO_API}/health")
    _check_response_validity(api_health)
    if api_health.json()["status"] == "UP":
        status = True
    else:
        status = False

    return status


def request_url_get(url: str) -> requests.models.Response:
    """
    Send GET request for a URL.

    Args:
        url (str): Link to request.

    Returns:
        requests.models.Response
    """
    add_dh_cipher_set()
    page = requests.get(url, verify=False)
    _check_response_validity(page)

    return page


def request_url_post(query: dict[str, str], **kwargs: Any) -> requests.models.Response:
    """
    Send POST request for URL.

    Args:
        url (str): Link to post request to
        query (dict[str, str]): Search criteria to filter request by.

    Returns:
        requests.models.Response
    """
    add_dh_cipher_set()
    url = f"{NEUROMORPHO_API}/neuron/select/"
    headers = {"Content-Type": "application/json"}

    page = requests.post(
        url,
        json=query,
        headers=headers,
        verify=False,
        **kwargs,
    )
    _check_response_validity(page)

    return page


def get_query_fields() -> set[str]:
    """Get list of accepted search fields."""
    return set(request_url_get(f"{NEUROMORPHO_API}/neuron/fields").json()["Neuron Fields"])


def get_query_values(field: str) -> set[str]:
    """Get list of accepted values for a given search field."""
    return set(request_url_get(f"{NEUROMORPHO_API}/neuron/fields/{field}").json()["fields"])


def validate_search(query: dict[str, str]) -> None:
    """Validate search query to ensure field and its items are acceptable."""
    query_fields = get_query_fields()
    print("Validating search query...")
    if not set(query.keys()).issubset(query_fields):
        raise ValueError(f"Invalid search field: {set(query.keys()) - query_fields}")

    for field, values in query.items():
        query_values = get_query_values(field)
        if not set(values).issubset(query_values):
            raise ValueError(f"Invalid field values for {field}: {set(values) - query_values}")


def _get_swc_url(neuron_name: str) -> str:
    """Get URL for a neuron's swc data from NeuroMorpho archives."""
    neuron_url = f"{NEURON_INFO}{neuron_name}"
    neuron_page = request_url_get(neuron_url)

    pattern = re.compile(r"<a href=(dableFiles/.*)>Morphology File \(Standardized\)</a>")
    match = re.findall(pattern, neuron_page.text)[0]

    return f"{NEUROMORPHO}/{match}"


class NeuroMorpho:
    """
    Access NeuroMorpho API to get neuron reconstructions.

    Attributes:
        valid_field_names (set): Set containing the valid field names to use for a query.
        neuron_list (list): List of neuron metadata in json

    """

    def __init__(self) -> None:
        if check_api_status():
            self.valid_field_names: set[str] = get_query_fields()
            # self.neuron_list: list[dict[str, Any]] = []
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

    def get_neuron_metadata(self, query: dict[str, str]) -> pd.DataFrame:
        """
        Get list of neurons from a search query.

        See list of query keys here: https://neuromorpho.org/api/neuron/fields

        Args:
            query (dict[str, str]): query values to filter neurons

        Returns:
            list[dict]: list of dicts where each dict is a single neuron's metadata.
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

        self.neuron_list = neuron_list
        self.neuron_metadata = pd.DataFrame(neuron_list)

        return self.neuron_metadata

    def get_neuron_swc(self, neuron_name: str) -> pd.DataFrame:
        """
        Create DataFrame of swc data for neuron using neuron_name.

        Args:
            neuron_name (str): name of neuron

        Returns:
            pd.DataFrame: swc data
        """
        swc_resp = request_url_get(_get_swc_url(neuron_name))
        response_text = io.StringIO(swc_resp.text)
        response_list = response_text.readlines()
        num_lines = next(idx for idx, line in enumerate(response_list) if "#" not in line)

        raw_swc_data = pd.DataFrame(response_list[num_lines:])
        swc_data = raw_swc_data[0].str.replace("\r\n", "").str.split(expand=True)
        col_names = dict(zip(swc_data.columns, ["id", "type", "x", "y", "z", "radius", "parent"]))
        swc_data.rename(columns=col_names, inplace=True)
        # set dtypes
        swc_data = swc_data.astype(
            {
                "id": int,
                "type": int,
                "x": float,
                "y": float,
                "z": float,
                "radius": float,
                "parent": int,
            }
        )

        return swc_data

    def download_swc_data(self) -> None:
        """Look up neuron name and retrieve swc data from NeuroMorpho."""
        assert self.neuron_metadata.empty is False, "No metadata!"

        print(f"Downloading swc data for {len(self.neuron_metadata['neuron_name'])} neurons...")

        for n, neuron in enumerate(self.neuron_metadata["neuron_name"]):
            if n % 100 == 0:
                print(f"loading neuron: {n}")
            with contextlib.suppress(ValueError):
                self.swc_data[neuron] = self.get_neuron_swc(neuron_name=neuron)

    def export_metadata(self, data_path: str, query_name: str) -> None:
        """
        Export metadata as csv.

        Args:
            data_path (str): export path
            query_name (str): name of metadata file
        """
        self.neuron_metadata.to_csv(f"{Path(data_path)}/{query_name}.csv", index=False)

    def export_swc_data(self, data_path: str, swc_filename: str) -> None:
        """
        Export dict of swc data to pkl file.

        Args:
            data_path (str): export path
            swc_filename (str): name of pkl file
        """
        with open(f"{Path(data_path)}/{swc_filename}.pkl", "wb") as f:
            pickle.dump(self.swc_data, f, protocol=-1)
