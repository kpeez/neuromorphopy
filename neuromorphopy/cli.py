#!/usr/bin/env python3
"""Command line interface for neuromorphopy."""

import asyncio
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.table import Table

from neuromorphopy import NeuroMorphoClient, Query, QueryFields, search_and_download

from .utils import get_logger, setup_logging

app = typer.Typer(
    help="Search and download neuron morphologies from NeuroMorpho.org",
    add_completion=True,
)
console = Console()


async def _preview_download(
    query_dict: dict[str, Any],
    output_dir: Path,
    metadata_filename: str,
) -> None:
    """Async preview function."""
    async with NeuroMorphoClient() as client:
        # get endpoint, total count, and query string using the shared helper
        try:
            endpoint, total, query_str = await client._get_search_details(query_dict)
        except Exception as e:
            console.print(f"[bold red]Error fetching total count during preview:[/] {e}")
            raise

        params_sample: dict[str, Any] = {"page": 0, "size": 3}
        if query_str is not None:
            params_sample["q"] = query_str

        # add sort parameter if it exists in the original query
        sort_info = query_dict.get("_sort")
        if isinstance(sort_info, dict) and "field" in sort_info and "order" in sort_info:
            params_sample["sort"] = f"{sort_info['field']},{sort_info['order']}"

        try:
            async with client.session.get(endpoint, params=params_sample) as response:
                response.raise_for_status()
                data = await response.json()
                sample = data.get("_embedded", {}).get("neuronResources", [])
        except Exception as e:
            console.print(f"[bold red]Error fetching sample during preview:[/] {e}")
            sample = []  # Set sample to empty list on error

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


def preview_download(query: dict[str, Any], output_dir: Path, metadata_filename: str) -> None:
    """Synchronous wrapper for preview."""
    try:
        asyncio.run(_preview_download(query, output_dir, metadata_filename))
    except Exception as err:
        console.print(f"[bold red]Error during preview:[/] {err}")
        raise typer.Exit(code=1) from err


@app.command("fields")
def fields(
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
            table.add_column("Available fields for filtering", style="green")
            for f in sorted(fields):
                table.add_row(f)
            console.print(table)
    except Exception as err:
        console.print(f"[bold red]Error:[/] {err}")
        raise typer.Exit(code=1) from err


@app.command("preview")
def preview(
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
        help="Directory where data *would* be saved (for preview)",
        resolve_path=True,
    ),
    metadata_filename: str = typer.Option(
        "metadata.csv",
        "--metadata-filename",
        "-m",
        help="Name for the metadata CSV file (for preview)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output during validation",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress validation output except errors",
    ),
) -> None:
    """Validate a query file and preview the download without downloading."""
    output_dir = output_dir if output_dir is not None else Path.cwd() / "neurons"

    try:
        if not quiet:
            console.print("[cyan]Validating query...[/cyan]")
        validate(query_file, quiet=not verbose)
        query = Query.from_file(query_file)
        preview_download(query, output_dir, metadata_filename)

    except Exception as err:
        if not isinstance(err, typer.Exit):
            raise typer.Exit(code=1) from err
        raise err


@app.command("download")
def download(
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
    group_by: str = typer.Option(
        None,
        "--group-by",
        "-g",
        help="Organize downloads by fields (comma-separated)",
    ),
) -> None:
    """Search NeuroMorpho.org and download matching neurons based on a query file."""
    output_dir = output_dir if output_dir is not None else Path.cwd() / "neurons"

    try:
        if not quiet:
            console.print("[cyan]Validating query...[/cyan]")
        validate(query_file, quiet=not verbose)
        query = Query.from_file(query_file)

        setup_logging(
            verbose=verbose,
            quiet=quiet,
            log_to_file=not no_log,
            output_dir=output_dir,
            query_file=query_file,
        )
        logger = get_logger()
        logger.debug(f"Loaded query from {query_file}")

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


def _validate_file_format(query_file: Path, table: Table) -> dict:
    """Validate the basic file format and structure."""
    with open(query_file, encoding="utf-8") as f:
        raw_query = yaml.safe_load(f)

    if not isinstance(raw_query, dict):
        table.add_row("File Format", "✗", "Query must be a dictionary")
        raise ValueError("Query must be a dictionary")

    if "filters" not in raw_query:
        table.add_row("Query Structure", "✗", "No filters specified")
        raise ValueError("Query must contain filters")

    table.add_row("File Format", "✓", f"Valid {query_file.suffix} format")
    table.add_row("Query Structure", "✓", "Valid query structure")

    return raw_query


def _validate_sort_config(raw_query: dict, table: Table) -> None:
    """Validate sort configuration if present."""
    if "sort" not in raw_query:
        return

    sort_config = raw_query["sort"]
    if not isinstance(sort_config, dict) or "field" not in sort_config:
        table.add_row("Sort Config", "✗", "Invalid sort configuration")
        raise ValueError("Invalid sort configuration")

    sort_field = sort_config["field"]
    if sort_field not in QueryFields.get_fields():
        table.add_row("Sort Config", "✗", f"Invalid sort field: {sort_field}")
        raise ValueError(f"Sort field '{sort_field}' is not a valid field")

    table.add_row("Sort Config", "✓", f"Valid sort configuration using field: {sort_field}")


def _validate_fields_and_values(query: dict, table: Table) -> None:
    """Validate all fields and their values."""
    invalid_fields = []
    for field, values in query.items():
        if field not in QueryFields.get_fields():
            continue  # Skip non-field keys like sort configuration

        valid_values = QueryFields.get_values(field)
        invalid_values = set(values) - valid_values
        if invalid_values:
            invalid_fields.append(f"{field}: invalid values {invalid_values}")

    if invalid_fields:
        table.add_row("Fields & Values", "✗", f"Invalid: {', '.join(invalid_fields)}")
        raise ValueError("Invalid fields or values found")

    table.add_row("Fields & Values", "✓", "All fields and values are valid")


def validate(
    query_file: Path,
    quiet: bool = False,
) -> tuple[bool, Table]:
    """Validate a query file's format, fields, and values.

    Raises:
        typer.Exit: If validation fails.
    """
    console = Console()
    table = Table(title="Query Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    try:
        raw_query = _validate_file_format(query_file, table)
        _validate_sort_config(raw_query, table)

        query = Query.from_file(query_file)
        _validate_fields_and_values(query, table)

        if not quiet:
            console.print(table)
            console.print("\n[green]Query validation successful! ✓[/green]")

        return True, table

    except Exception as err:
        if not quiet:
            console.print(table)
            console.print(f"\n[bold red]Validation failed: {err}[/bold red]")
        # Ensure the original error is re-raised correctly, wrapped in typer.Exit if needed
        if isinstance(err, typer.Exit):
            raise err
        else:
            raise typer.Exit(code=1) from err


def main() -> None:
    """Run the CLI application."""
    app(prog_name="neuromorpho")


if __name__ == "__main__":
    main()
