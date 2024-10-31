import asyncio
import logging
import ssl
from pathlib import Path
from typing import Any

import aiohttp
import pandas as pd
from tqdm.asyncio import tqdm

from .io.swc import get_swc_url
from .utils import NEUROMORPHO_API, clean_metadata_columns, generate_grouped_path


class NeuroMorphoClient:
    def __init__(
        self,
        max_concurrent: int = 20,
        max_connections: int = 100,
    ):
        self.base_url = NEUROMORPHO_API
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.set_ciphers("DEFAULT:@SECLEVEL=1")
        self.max_concurrent = max_concurrent
        self.connector = aiohttp.TCPConnector(
            limit=max_connections, limit_per_host=max_concurrent, ssl=self.ssl_context
        )

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(connector=self.connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _fetch_page(self, query_str: str, page: int, size: int) -> list[dict[str, Any]]:
        """Fetch a single page of results."""
        params = {"page": page, "size": size, "q": query_str}
        async with self.session.get(f"{self.base_url}/neuron/select", params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data["_embedded"]["neuronResources"]

    async def search_neurons(
        self,
        query: dict[str, list[str]],
        output_dir: Path | None = None,
        metadata_filename: str = "neuron_metadata.csv",
        show_progress: bool = True,
    ) -> list[dict[str, Any]]:
        """Search for neurons with concurrent pagination and progress bar.

        Args:
            query: Search query parameters
            output_dir: Optional directory to save metadata CSV
            metadata_filename: Name of the metadata file
            show_progress: Whether to show progress bar

        Returns:
            List of neuron dictionaries
        """
        # Get total count first
        query_str = " ".join(f"{field}:{','.join(values)}" for field, values in query.items())
        params = {"page": 0, "size": 1, "q": query_str}

        async with self.session.get(f"{self.base_url}/neuron/select", params=params) as response:
            response.raise_for_status()
            data = await response.json()
            total = data["page"]["totalElements"]

        size = 100
        pages = (total + size - 1) // size
        sem = asyncio.Semaphore(self.max_concurrent)

        async def fetch_with_sem(page: int) -> list[dict[str, Any]]:
            async with sem:
                return await self._fetch_page(query_str, page, size)

        tasks = [fetch_with_sem(page) for page in range(pages)]
        if show_progress:
            results = await tqdm.gather(*tasks, desc="Fetching neurons")
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
        # Run the synchronous function in a thread pool to avoid blocking the event loop
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

                # Generate target path based on grouping
                if group_by:
                    target_dir = generate_grouped_path(downloads_dir, neuron, group_by)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    output_path = target_dir / f"{name}.swc"
                else:
                    output_path = downloads_dir / f"{name}.swc"

                # Skip if already downloaded
                if output_path.exists():
                    logger.debug(f"Skipping {name}: already downloaded")
                    return

                try:
                    async with (
                        aiohttp.ClientSession() as session,
                        session.get(await self.get_swc_url(name), ssl=self.ssl_context) as response,
                    ):
                        response.raise_for_status()
                        content = await response.text()
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
    query: dict[str, list[str]],
    output_dir: Path,
    metadata_filename: str = "neuron_metadata.csv",
    max_concurrent: int = 20,
    group_by: str | None = None,
) -> None:
    """Convenience function for synchronous usage.

    Args:
        query: Search query parameters
        output_dir: Base directory for all data
        metadata_filename: Name of the metadata file
        max_concurrent: Maximum concurrent operations
        group_by: Optional comma-separated list of fields to group downloads by
    """

    async def _run():
        async with NeuroMorphoClient(max_concurrent=max_concurrent) as client:
            # Search and save metadata to base directory
            neurons = await client.search_neurons(
                query, output_dir=output_dir, metadata_filename=metadata_filename
            )

            # If group_by is specified, modify the output directory structure
            if group_by:
                downloads_dir = output_dir / "downloads"
                for neuron in neurons:
                    target_dir = generate_grouped_path(downloads_dir, neuron, group_by)
                    target_dir.mkdir(parents=True, exist_ok=True)

            await client.download_neurons(neurons, output_dir, max_concurrent=max_concurrent, group_by=group_by)
            return len(neurons)

    count = asyncio.run(_run())
    print(f"Downloaded {count} neurons to {output_dir}/downloads")
