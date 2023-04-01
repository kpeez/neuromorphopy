"""Process swc data from NeuroMorpho."""
import datetime
import io
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

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


def download_swc_data(
    neuron_list: list[str] | pd.Series,
    download_dir: str | Path | None = None,
) -> None:
    """Download swc data from list of neurons on NeuroMorpho.

    This function will create a directory in the ``download_dir`` (or current working directory
    if no directory is provided). All neurons in the ``neuron_list`` will be saved here.

    Args:
        neuron_list (list[str] | pd.Series[str]): List of neuron names to retrieve swc data for.
        download_dir (str | Path): Path to download swc data to. If None, will download to
        current working directory.
    """
    print(f"Downloading swc data for {len(neuron_list)} neurons.")

    download_dirname = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M-swc_files")

    download_path = (
        Path.cwd() / download_dirname
        if not download_dir
        else Path(f"{download_dir}/{download_dirname}")
    )

    if not download_path.exists():
        download_path.mkdir(parents=True)

    num_iterations = len(neuron_list)
    percent_increment = 5
    increment_value = int(num_iterations * percent_increment / 100)

    with tqdm(
        total=num_iterations,
        desc="Downloading neurons",
        bar_format="{desc}[{n_fmt}/{total_fmt}]{percentage:3.0f}%|{bar}"
        "{postfix} [{elapsed}<{remaining}]",
    ) as pbar:
        for n, neuron in enumerate(neuron_list):
            try:
                swc_data = get_neuron_swc(neuron_name=neuron)
                swc_data.to_csv(f"{download_path}/{neuron}.swc", sep=" ", header=True, index=False)
            except Exception as e:
                print(f"Error downloading {neuron}: {e}")
            if n % increment_value == 0:
                pbar.update(increment_value)
