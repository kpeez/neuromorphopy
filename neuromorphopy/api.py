import asyncio
import logging
from pathlib import Path
from typing import Any, Type

import httpx
import pandas as pd
from tqdm.asyncio import tqdm

from .exceptions import ApiError
from .io.swc import get_swc_url
from .utils import (
    NEUROMORPHO_API,
    clean_metadata_columns,
    generate_grouped_path,
    get_neuromorpho_ssl_context,
)


class NeuroMorphoClient:
    def __init__(
        self,
        max_concurrent: int = 20,
        max_connections: int = 100,
    ):
        self.base_url = NEUROMORPHO_API
        self.max_concurrent = max_concurrent
        # Connection limits
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_concurrent,
        )
        self.ssl_context = get_neuromorpho_ssl_context()
        self.session: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "NeuroMorphoClient":
        self.session = httpx.AsyncClient(
            limits=self.limits,
            verify=self.ssl_context,
            timeout=60.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if self.session:
            await self.session.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the underlying httpx AsyncClient."""
        if self.session is None:
            raise RuntimeError("Session not initialized. Use 'async with NeuroMorphoClient()'.")
        return self.session

    async def _get_search_details(self, query: dict[str, Any]) -> tuple[str, int, str | None]:
        """Determine endpoint, query string, and total count for a search."""
        # separate sort info from filters
        filters = {k: v for k, v in query.items() if k != "_sort"}
        sort_info = query.get("_sort")

        params_count: dict[str, Any] = {"page": 0, "size": 1}
        query_str: str | None = None

        if not filters:
            endpoint = f"{self.base_url}/neuron"
        else:
            endpoint = f"{self.base_url}/neuron/select"
            query_str = " ".join(f"{field}:{','.join(values)}" for field, values in filters.items())
            params_count["q"] = query_str

        if sort_info:
            params_count["sort"] = f"{sort_info['field']},{sort_info['order']}"

        logging.info(f"Fetching total count from {endpoint} with params: {params_count}")
        try:
            response = await self.client.get(endpoint, params=params_count)
            response.raise_for_status()
            data = response.json()

            if (
                isinstance(data, dict)
                and "page" in data
                and isinstance(data["page"], dict)
                and "totalElements" in data["page"]
            ):
                total = int(data["page"]["totalElements"])
                return endpoint, total, query_str
            else:
                error_message = f"Unexpected API response format when fetching count. Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}. Response: {data}"
                logging.error(error_message)
                raise ApiError(error_message, status_code=response.status_code)

        except httpx.HTTPStatusError as e:
            # catch HTTP errors specifically to include status code
            logging.error(f"HTTP Error fetching total count: {e.response.status_code} - {e}")
            raise ApiError(
                f"HTTP Error: {e.response.status_code} - {e}", status_code=e.response.status_code
            ) from e
        except Exception as e:
            logging.error(f"Error fetching total count: {e!s}")
            raise

    async def _fetch_page(
        self, endpoint: str, page: int, size: int, query_str: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch a single page of results from a given endpoint."""
        params: dict[str, str | int] = {"page": page, "size": size}
        if query_str is not None:
            params["q"] = query_str

        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        return data.get("_embedded", {}).get("neuronResources", [])

    async def search_neurons(
        self,
        query: dict[str, Any],
        output_dir: Path | None = None,
        metadata_filename: str = "neuron_metadata.csv",
        show_progress: bool = True,
    ) -> list[dict[str, Any]]:
        """Search for neurons with concurrent pagination and progress bar.

        Uses /neuron if query is empty, /neuron/select otherwise.

        Args:
            query: Search query parameters
            output_dir: Optional directory to save metadata CSV
            metadata_filename: Name of the metadata file
            show_progress: Whether to show progress bar

        Returns:
            List of neuron dictionaries
        """
        size = 100  # page size for fetching results
        sem = asyncio.Semaphore(self.max_concurrent)

        # get endpoint, total count, and query string using the helper method
        try:
            endpoint, total, query_str = await self._get_search_details(query)
        except Exception:
            return []  # error already logged in helper

        if total == 0:
            print("No neurons found matching the criteria.")
            return []

        print(f"Found {total} neurons. Fetching details...")
        pages = (total + size - 1) // size

        async def fetch_with_sem(page: int) -> list[dict[str, Any]]:
            async with sem:
                return await self._fetch_page(endpoint, page, size, query_str)

        tasks = [fetch_with_sem(page) for page in range(pages)]
        results: list[list[dict[str, Any]]]
        if show_progress:
            results = await tqdm.gather(*tasks, desc="Fetching neurons", total=pages)
        else:
            results = await asyncio.gather(*tasks)

        neurons = [neuron for page_results in results for neuron in page_results]

        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            print("Processing metadata...")
            df = pd.DataFrame(neurons)
            df = clean_metadata_columns(df)

            metadata_path = output_dir / metadata_filename
            df.to_csv(metadata_path, index=False)
            print(f"Saved metadata for {len(neurons)} neurons to {metadata_path}")

        return neurons

    @staticmethod
    async def get_swc_url(neuron_name: str) -> str:
        """Get the SWC file URL for a neuron."""
        # run the synchronous function in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_swc_url, neuron_name)

    async def download_neurons(
        self,
        neurons: list[dict[str, Any]],
        output_dir: Path,
        max_concurrent: int | None = None,
        show_progress: bool = True,
        group_by: str | None = None,
    ) -> None:
        """Download SWC files for multiple neurons.

        Args:
            neurons: List of neuron dictionaries from search_neurons
            output_dir: Base directory for downloads
            max_concurrent: Override default concurrent downloads
            show_progress: Whether to show progress bar
            group_by: Optional comma-separated list of fields to group downloads by
        """
        output_dir = Path(output_dir)
        downloads_dir = output_dir / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)

        download_semaphore = asyncio.Semaphore(max_concurrent or self.max_concurrent)

        async def download_one(neuron: dict[str, Any]) -> None:
            async with download_semaphore:
                name = neuron["neuron_name"]
                logger = logging.getLogger("neuromorphopy")

                # generate target path based on grouping
                if group_by:
                    target_dir = generate_grouped_path(downloads_dir, neuron, group_by)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    output_path = target_dir / f"{name}.swc"
                else:
                    output_path = downloads_dir / f"{name}.swc"

                # skip if already downloaded
                if output_path.exists():
                    logger.debug(f"Skipping {name}: already downloaded")
                    return

                try:
                    # use the shared session from the client
                    url = await self.get_swc_url(name)
                    response = await self.client.get(url)
                    response.raise_for_status()
                    content = response.text
                    output_path.write_text(content)
                    logger.info(f"Downloaded {name} to {output_path}")
                except Exception as e:
                    logger.error(f"Error downloading {name}: {e}")

        tasks = [download_one(n) for n in neurons]
        if show_progress:
            await tqdm.gather(*tasks, desc="Downloading neurons")
        else:
            await asyncio.gather(*tasks)


def search_and_download(
    query: dict[str, Any],
    output_dir: Path,
    metadata_filename: str = "neuron_metadata.csv",
    max_concurrent: int = 20,
    group_by: str | None = None,
) -> int:
    """Convenience function for synchronous usage.

    Args:
        query: Search query parameters
        output_dir: Base directory for all data
        metadata_filename: Name of the metadata file
        max_concurrent: Maximum concurrent operations
        group_by: Optional comma-separated list of fields to group downloads by
    """

    async def _run() -> int:
        async with NeuroMorphoClient(max_concurrent=max_concurrent) as client:
            # search and save metadata to base directory
            neurons = await client.search_neurons(
                query=query, output_dir=output_dir, metadata_filename=metadata_filename
            )

            # if group_by is specified, modify the output directory structure
            if group_by:
                downloads_dir = output_dir / "downloads"
                for neuron in neurons:
                    target_dir = generate_grouped_path(downloads_dir, neuron, group_by)
                    target_dir.mkdir(parents=True, exist_ok=True)

            await client.download_neurons(
                neurons, output_dir, max_concurrent=max_concurrent, group_by=group_by
            )

            return len(neurons)

    # capture the count returned by _run
    count = asyncio.run(_run())
    print(f"Downloaded {count} neurons to {output_dir}/downloads")

    return count
