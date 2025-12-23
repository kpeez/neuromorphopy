"""Utility functions for NeuroMorpho API.

This module handles API communication with NeuroMorpho.org, including special SSL handling
required due to their server configuration.

SSL Configuration:
    The NeuroMorpho.org server uses older SSL settings that require specific handling:
    1. Weak DH keys that modern Python rejects by default
    2. Self-signed certificates in the certificate chain
    3. Multiple layers of SSL verification that need to be disabled

    To handle this, we:
        - Use a custom SSLContext with weaker security settings
        - Disable certificate verification
        - Configure ciphers to accept weaker DH keys

Note:
    While disabling SSL verification is generally not recommended, it's necessary
    for accessing the NeuroMorpho data API.
"""

import ssl
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

NEUROMORPHO = "https://neuromorpho.org"
NEUROMORPHO_API = "https://neuromorpho.org/api"
NEURON_INFO = f"{NEUROMORPHO}/neuron_info.jsp?neuron_name="


def get_neuromorpho_ssl_context() -> ssl.SSLContext:
    """Create an SSL context compatible with NeuroMorpho's legacy security settings."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Allow weak DH keys (SECLEVEL=1)
    context.set_ciphers("DEFAULT:@SECLEVEL=1")
    return context


# create shared client with custom SSL context
client = httpx.Client(
    verify=get_neuromorpho_ssl_context(),
    timeout=60.0,
    follow_redirects=True,
)


def request_url_get(url: str, **kwargs: Any) -> httpx.Response:
    """Send GET request for a URL."""
    response = client.get(url, **kwargs)
    _check_response_validity(response)
    return response


def request_url_post(query: dict[str, list[str]], **kwargs: Any) -> httpx.Response:
    """Send POST request."""
    url = f"{NEUROMORPHO_API}/neuron/select/"
    # httpx automatically sets Content-Type when using json parameter
    response = client.post(url, json=query, **kwargs)
    _check_response_validity(response)
    return response


def _check_response_validity(response: httpx.Response) -> None:
    """Check if response is valid."""
    if not response.is_success:
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
