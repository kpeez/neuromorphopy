"""Utility functions for NeuroMorpho API.

This module handles API communication with NeuroMorpho.org, including special SSL handling
required due to their server configuration.

SSL Configuration:
    The NeuroMorpho.org server uses older SSL settings that require specific handling:
    1. Weak DH keys that modern Python rejects by default
    2. Self-signed certificates in the certificate chain
    3. Multiple layers of SSL verification that need to be disabled

    To handle this, we:
        - Use a custom HTTPAdapter with modified SSL context
        - Disable certificate verification at multiple levels
        - Configure ciphers to accept weaker DH keys
        - Suppress insecure connection warnings

Note:
    While disabling SSL verification is generally not recommended, it's necessary
    for accessing the NeuroMorpho data API.
"""

import ssl
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context

NEUROMORPHO = "https://neuromorpho.org"
NEUROMORPHO_API = "https://neuromorpho.org/api"
NEURON_INFO = f"{NEUROMORPHO}/neuron_info.jsp?neuron_name="


class WeakDHAdapter(HTTPAdapter):
    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> PoolManager:
        context = create_urllib3_context()
        # disable ALL verification
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        pool_kwargs["ssl_context"] = context
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)


# disable SSL verification warnings globally
urllib3.disable_warnings(InsecureRequestWarning)

# create session with custom adapter
session = requests.Session()
session.verify = False
adapter = WeakDHAdapter()
session.mount("https://", adapter)


def request_url_get(url: str, **kwargs: Any) -> requests.Response:
    """Send GET request for a URL."""
    response = session.get(url, verify=False, **kwargs)
    _check_response_validity(response)
    return response


def request_url_post(query: dict[str, list[str]], **kwargs: Any) -> requests.Response:
    """Send POST request."""
    url = f"{NEUROMORPHO_API}/neuron/select/"
    headers = {"Content-Type": "application/json"}
    kwargs["verify"] = False
    response = session.post(url, json=query, headers=headers, **kwargs)
    _check_response_validity(response)
    return response


def _check_response_validity(response: requests.Response) -> None:
    """Check if response is valid."""
    if not response.ok:
        raise ValueError(f"Request failed: {response.status_code} - {response.text}")


def clean_metadata_columns(metadata: pd.DataFrame) -> pd.DataFrame:
    """Clean columns of dataframe using vectorized operations."""
    df = metadata.copy()

    def clean_str_column(col: pd.Series) -> pd.Series:
        if not pd.api.types.is_string_dtype(col):
            col = col.astype(str)

        return (
            col.str.strip("[]")
            .str.replace("'", "", regex=False)
            .str.replace("layer ", "", regex=False)
            .str.replace(r"(?<=\w)[, ](?=\w)", "_", regex=True)
            .str.lower()
        )

    mask = (pd.api.types.is_object_dtype(df.dtypes)) & (df.columns != "neuron_name")
    for col_name in df.columns[mask]:
        df[col_name] = clean_str_column(df[col_name])

    return df


def generate_grouped_path(base_dir: Path, neuron_data: dict[str, Any], group_by: str) -> Path:
    """Generate a grouped directory path based on neuron metadata.

    Args:
        base_dir: Base directory for the grouped structure
        neuron_data: Dictionary containing neuron metadata
        group_by: Comma-separated list of fields to group by

    Returns:
        Path object representing the grouped directory structure
    """
    path_parts: list[Path] = [base_dir]
    for field in group_by.split(","):
        field = field.strip()
        if field in neuron_data:
            # sanitize the field value for filesystem use
            safe_value = str(neuron_data[field]).replace("/", "_").replace("\\", "_")
            path_parts.append(Path(safe_value))

    return Path(*path_parts)
