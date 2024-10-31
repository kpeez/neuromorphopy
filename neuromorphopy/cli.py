#!/usr/bin/env python3
"""Command line interface for neuromorphopy."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from neuromorphopy import NeuroMorphoClient, Query, QueryFields, search_and_download

from .utils import NEUROMORPHO_API, get_logger, setup_logging

app = typer.Typer(
    help="Search and download neuron morphologies from NeuroMorpho.org",
    add_completion=True,
)
console = Console()


async def _preview_download(
    query_dict: dict[str, list[str]],
    output_dir: Path,
    metadata_filename: str,
) -> None:
    """Async preview function."""
    async with NeuroMorphoClient() as client:
        # Get total count first
        query_str = " ".join(f"{field}:{','.join(values)}" for field, values in query_dict.items())
        params = {"page": 0, "size": 1, "q": query_str}

        async with client.session.get(
            f"{NEUROMORPHO_API}/neuron/select", params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()
            total = data["page"]["totalElements"]

        # Get sample
        params["size"] = 3
        async with client.session.get(
            f"{NEUROMORPHO_API}/neuron/select", params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()
            sample = data["_embedded"]["neuronResources"]

        table = Table(title="Download Preview")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total neurons", str(total))
        table.add_row("Output directory", str(output_dir))
        table.add_row("Metadata file", metadata_filename)

        if sample:
            table.add_section()
            table.add_row("Sample neurons", sample[0]["neuron_name"])
            for neuron in sample[1:]:
                table.add_row("", neuron["neuron_name"])

        console.print(table)


def preview_download(query: Query, output_dir: Path, metadata_filename: str) -> None:
    """Synchronous wrapper for preview."""
    try:
        asyncio.run(_preview_download(query, output_dir, metadata_filename))
    except Exception as err:
        console.print(f"[bold red]Error during preview:[/] {err}")
        raise typer.Exit(code=1) from err


@app.command()
def search(
    query_file: Path = typer.Argument(  # noqa: B008
        ...,
        help="Path to YAML/JSON query file",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(  # noqa: B008
        None,
        "--output-dir",
        "-o",
        help="Directory to save downloaded data",
        resolve_path=True,
    ),
    metadata_filename: str = typer.Option(
        "metadata.csv",
        "--metadata-filename",
        "-m",
        help="Name for the metadata CSV file",
    ),
    concurrent: int = typer.Option(
        20,
        "--concurrent",
        "-c",
        help="Maximum concurrent downloads",
        min=1,
        max=50,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all output except errors",
    ),
    no_log: bool = typer.Option(
        False,
        "--no-log",
        help="Disable writing to log file",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be downloaded without downloading",
    ),
    group_by: str = typer.Option(
        None,
        "--group-by",
        "-g",
        help="Organize downloads by fields (comma-separated)",
    ),
) -> None:
    """Search and download neurons based on a query file."""
    if output_dir is None:
        output_dir = Path.cwd() / "neurons"
    setup_logging(
        verbose=verbose,
        quiet=quiet,
        log_to_file=not no_log,
        output_dir=output_dir,
        query_file=query_file,
    )
    logger = get_logger()

    try:
        query = Query.from_file(query_file)
        logger.debug(f"Loaded query from {query_file}")

        if dry_run:
            preview_download(query, output_dir, metadata_filename)
            return

        logger.info("Starting download...")
        search_and_download(
            query=query,
            output_dir=output_dir,
            metadata_filename=metadata_filename,
            max_concurrent=concurrent,
            group_by=group_by,
        )
        logger.info("Download complete!")

    except Exception as err:
        logger.error(f"Error: {err}")
        raise typer.Exit(code=1) from err


@app.command()
def explore(
    field: str | None = typer.Argument(
        None,
        help="Show valid values for a specific field",
    ),
) -> None:
    """Explore available query fields and their values."""
    try:
        if field:
            values = QueryFields.get_values(field)
            table = Table(title=f"Valid values for {field}")
            table.add_column("Value", style="cyan")
            for value in sorted(values):
                table.add_row(str(value))
            console.print(table)
        else:
            fields = QueryFields.get_fields()
            table = Table(title="Available query fields")
            table.add_column("Field", style="green")
            for f in sorted(fields):
                table.add_row(f)
            console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error:[/] {err}")
        raise typer.Exit(code=1) from err


def main() -> None:
    """Run the CLI application."""
    app(prog_name="neuromorpho")


if __name__ == "__main__":
    main()
