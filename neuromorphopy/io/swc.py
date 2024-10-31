"""Process swc data from NeuroMorpho."""

import datetime
import io
import re
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from tqdm import tqdm

from neuromorphopy.utils import NEUROMORPHO, NEURON_INFO, request_url_get

if TYPE_CHECKING:
    from collections.abc import Sequence


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
    processed_data = [
        re.split(r"\s+", line.strip()) for line in response_list if not line.startswith("#")
    ]
    swc_data = pd.DataFrame(
        processed_data, columns=["n", "type", "x", "y", "z", "radius", "parent"]
    )
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


def download_neuron_data(neuron: str, download_path: Path) -> str:
    try:
        swc_data = get_neuron_swc(neuron_name=neuron)
        file_path = f"{download_path}/{neuron}.swc"
        with open(file_path, "w", encoding="utf-8") as file:
            header = " ".join(swc_data.columns)
            file.write(f"# {header}\n")
        swc_data.to_csv(file_path, mode="a", index=False, sep=" ", header=False)
        return f"Downloaded {neuron}"
    except Exception as e:
        return f"Error downloading {neuron}: {e}"


def download_swc_data(
    neuron_list: Sequence[str],
    download_dir: str | Path | None = None,
) -> None:
    """Download swc data from list of neurons on NeuroMorpho using parallel processing.

    Args:
        neuron_list (Sequence[str]): List of neuron names to retrieve swc data for.
        download_dir (str | Path | None): Path to download swc data to. If None, will download to
        current working directory. Defaults to None.
    """
    download_dirname = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M-swc_files")
    download_path = (
        Path.cwd() / download_dirname
        if not download_dir
        else Path(f"{download_dir}/{download_dirname}")
    )

    if not download_path.exists():
        download_path.mkdir(parents=True)

    downloaded_neurons = [f.stem for f in download_path.rglob("*.swc")]
    neurons = list(set(neuron_list) - set(downloaded_neurons))

    with ThreadPoolExecutor() as executor:
        tasks = {
            executor.submit(download_neuron_data, neuron, download_path): neuron
            for neuron in neurons
        }
        for _ in tqdm(as_completed(tasks), total=len(tasks), desc="Downloading neurons"):
            pass
