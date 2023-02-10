"""Process swc data from NeuroMorpho."""
import contextlib
import io
import re

import pandas as pd

from neuromorphopy.utils import NEUROMORPHO, NEURON_INFO, request_url_get


def get_swc_url(neuron_name: str) -> str:
    """Get URL for a neuron's swc data from NeuroMorpho archives."""
    neuron_url = f"{NEURON_INFO}{neuron_name}"
    neuron_page = request_url_get(neuron_url)

    pattern = re.compile(r"<a href=(dableFiles/.*)>Morphology File \(Standardized\)</a>")
    match = re.findall(pattern, neuron_page.text)[0]

    return f"{NEUROMORPHO}/{match}"


def validate_swc_data(swc_data: pd.DataFrame) -> None:
    """Ensure swc data is valid."""
    if -1 not in swc_data["parent"].unique():
        raise ValueError("SWC data does not contain a root node.")

    if 1 not in swc_data["type"].unique():
        print("SWC data does not contain a soma. Setting root node to type = 1 (soma).")
        swc_data.loc[0, "type"] = 1


def get_neuron_swc(neuron_name: str) -> pd.DataFrame:
    """Create DataFrame of swc data for neuron using neuron_name.

    Args:
        neuron_name (str): name of neuron

    Returns:
        pd.DataFrame: swc data
    """
    swc_resp = request_url_get(get_swc_url(neuron_name))
    response_text = io.StringIO(swc_resp.text)
    response_list = response_text.readlines()
    num_lines = next(idx for idx, line in enumerate(response_list) if "#" not in line)

    raw_swc_data = pd.DataFrame(response_list[num_lines:])
    swc_data = raw_swc_data[0].str.replace("\r\n", "").str.split(expand=True)
    col_names = dict(
        zip(swc_data.columns, ["n", "type", "x", "y", "z", "radius", "parent"], strict=True)
    )
    swc_data.rename(columns=col_names, inplace=True)
    # set dtypes
    swc_data = swc_data.astype(
        {
            "n": int,
            "type": int,
            "x": float,
            "y": float,
            "z": float,
            "radius": float,
            "parent": int,
        }
    )
    validate_swc_data(swc_data)

    return swc_data


def download_swc_data(neuron_list: list[str] | pd.Series) -> dict[str, pd.DataFrame]:
    """Look up neuron name and retrieve swc data from NeuroMorpho.

    Args:
        neuron_list (list[str] | pd.Series[str]): List of neuron names to retrieve swc data for.

    Returns:
        dict[str, pd.DataFrame]: Dictionary of neuron names and swc data.
    """
    print(f"Downloading swc data for {len(neuron_list)} neurons...")

    swc_data = {}
    for n, neuron in enumerate(neuron_list):
        if n % 100 == 0:
            print(f"loading neuron: {n}")
        with contextlib.suppress(ValueError):
            swc_data[neuron] = get_neuron_swc(neuron_name=neuron)

    return swc_data
