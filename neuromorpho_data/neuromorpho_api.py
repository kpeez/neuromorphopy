"""Work with NeuroMorpho API."""
import contextlib
import io
import re

import numpy as np
import pandas as pd
import requests

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
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH:!aNULL"

    with contextlib.suppress(AttributeError):
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += "HIGH:!DH:!aNULL"


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


def request_url_post(query: dict[str, str], **kwargs) -> requests.models.Response:
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

    page = requests.post(url, json=query, headers=headers, verify=False, **kwargs)
    _check_response_validity(page)

    return page


def _get_swc_url(neuron_name: str) -> str:
    """Get URL for a neuron's swc data from NeuroMorpho archives."""
    # neuron_url = f"{NEURON_INFO}{neuron['neuron_name']}"
    neuron_url = f"{NEURON_INFO}{neuron_name}"
    neuron_page = request_url_get(neuron_url)

    pattern = re.compile(r"<a href=(dableFiles/.*)>Morphology File \(Standardized\)</a>")
    match = re.findall(pattern, neuron_page.text)[0]

    return f"{NEUROMORPHO}/{match}"


def get_neuron_swc(neuron_name: str) -> pd.DataFrame:
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

    colnames = ["id", "type", "x", "y", "z", "radius", "parent"]
    raw_swc_data = pd.DataFrame(response_list[num_lines:])
    swc_data = raw_swc_data[0].str.replace("\r\n", "").str.split(expand=True)
    swc_data.columns = colnames
    # set dtypes
    col_dtypes = {
        "id": int,
        "type": int,
        "x": float,
        "y": float,
        "z": float,
        "radius": float,
        "parent": int,
    }
    swc_data = swc_data.astype(col_dtypes)

    return swc_data


def get_neuron_list(query: dict[str, str]) -> list[dict]:
    """
    Get list of neurons from a search query.

    See list of query keys here: https://neuromorpho.org/api/neuron/fields

    Args:
        query (dict[str, str]): query values to filter neurons

    Returns:
        list[dict]: list of dicts where each dict is a single neuron's metadata.
    """
    # use an initial request to get query info
    total_neurons = request_url_post(query).json()["page"]["totalElements"]
    num_pages = np.ceil(total_neurons / MAX_NEURONS).astype(int)

    neuron_list = []
    for page_idx in range(num_pages):
        neuron_count = MAX_NEURONS
        page = request_url_post(query, params={"size": neuron_count, "page": page_idx})
        neuron_list.extend(page.json()["_embedded"]["neuronResources"])

    return neuron_list


def get_swc_data(neuron_list: list[str]) -> dict[str, pd.DataFrame]:
    """
    Look up neuron name and retrieve swc data from NeuroMorpho.

    Args:
        neuron_list (list[str]): list of neuron names

    Returns:
        dict[str, pd.DataFrame]: swc data for each neuron in the input list.
    """
    print(f"Getting swc data for {len(neuron_list)} neurons.")

    swc_data: dict[str, pd.DataFrame] = {}
    for n, neuron in enumerate(neuron_list):
        if n % 100 == 0:
            print(f"loading neuron: {n}")
        with contextlib.suppress(ValueError):
            swc_data[neuron] = get_neuron_swc(neuron)

    return swc_data
