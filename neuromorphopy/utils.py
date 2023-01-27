"""Utilities for NeuroMorpho API."""
from __future__ import annotations
import pandas as pd
import json
import contextlib
import re
from typing import Any, no_type_check
from pathlib import Path
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util import ssl_

# globals
NEUROMORPHO = "https://neuromorpho.org"
NEUROMORPHO_API = "https://neuromorpho.org/api"
NEURON_INFO = f"{NEUROMORPHO}/neuron_info.jsp?neuron_name="


@no_type_check
def add_dh_cipher_set() -> None:
    """
    Update SSL cipher list to ignore DH KEY TOO SMALL error.

    See:
    https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small
    """
    disable_warnings(InsecureRequestWarning)
    ssl_.DEFAULT_CIPHERS += "HIGH:!DH:!aNULL"
    with contextlib.suppress(AttributeError):
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += "HIGH:!DH:!aNULL"


def _check_response_validity(page: requests.Response) -> None:
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


def request_url_get(url: str) -> requests.Response:
    """
    Send GET request for a URL.

    Args:
        url (str): Link to request.

    Returns:
        Response
    """
    add_dh_cipher_set()
    page = requests.get(url, verify=False)
    _check_response_validity(page)

    return page


def request_url_post(
    query: dict[str, list[str]],
    **kwargs: Any,
) -> requests.Response:
    """
    Send POST request for URL.

    Args:
        url (str): Link to post request to
        query (dict[str, str]): Search criteria to filter request by.

    Returns:
        Response
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


def get_image_url(neuron_name: str) -> str:
    """
    Get image url for neuron.

    Args:
        neuron_name (str): name of neuron

    Returns:
        str: image url
    """
    neuron_page = request_url_get(f"{NEURON_INFO}{neuron_name}")
    pattern = re.compile(r"./images/imageFiles/[^/]*/[^/]*\.png")
    match = re.findall(pattern, neuron_page.text)

    return f"{NEUROMORPHO}{match[0]}"


def load_json_query(query_file: str | Path) -> dict[str, list[str]]:
    """
    Load json query file.

    Args:
        query_file (str): Path to json query file.

    Returns:
        dict[str, list[str]]: Query dictionary.
    """
    with open(query_file, "r") as file:
        # Load the JSON data from the file
        query: dict[str, list[str]] = json.load(file)

    return query


def clean_str_column(col: pd.Series) -> pd.Series:
    """Clean a str column from DataFrame."""
    return (
        col.str.lstrip("[")
        .str.rstrip("]")
        .str.replace("'", "")
        .str.replace(", ", "_")
        .str.replace("layer ", "layer")
        .str.replace(" ", "_")
        .str.lower()
    )


def clean_metadata_columns(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Clean columns of dataframe.

    Args:
        metadata (pd.DataFrame): Dataframe to clean.

    Returns:
        pd.DataFrame: metadata with cleaned columns.
    """
    for col in metadata.columns:
        if metadata[col].dtype == "object" and col != "neuron_name":
            metadata[col] = clean_str_column(metadata[col].astype(str))
    return metadata
