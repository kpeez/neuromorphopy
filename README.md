# neuromorphopy

[![License](https://img.shields.io/github/license/kpeez/neuromorphopy)](https://img.shields.io/github/license/kpeez/neuromorphopy)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://neuromorphopy.readthedocs.io/)
[![PyPI](https://badge.fury.io/py/neuromorphopy.svg)](https://badge.fury.io/py/neuromorphopy)

<p align="left">
  <img src="https://raw.githubusercontent.com/kpeez/neuromorphopy/main/docs/assets/logo.png" width="350" alt="Neuromorphopy logo">
</p>

**neuromorphopy** is a lightweight, standalone Python CLI tool and library for efficiently searching and downloading neuron morphologies from the [NeuroMorpho.org](https://neuromorpho.org/) archives.

## Features

- **Efficient Downloads:** Uses asynchronous I/O (`httpx` + `asyncio`) for fast, concurrent downloads.
- **Flexible Querying:** Search using simple YAML or JSON configuration files.
- **Metadata Management:** Automatically cleans and saves neuron metadata to CSV.
- **Smart Validation:** Validates search queries against the API schema before execution.
- **Robust:** Handles legacy SSL requirements of the NeuroMorpho API automatically.

## Installation

`neuromorphopy` requires Python 3.11 or later.

### CLI Installation (Recommended)

The best way to install the tool for command-line use is with [`uv`](https://github.com/astral-sh/uv):

```bash
# Install the latest release
uv tool install neuromorphopy

# Or install the latest development version from GitHub
uv tool install git+https://github.com/kpeez/neuromorphopy.git
```

### Development Installation

To work on the codebase or run from source:

1. Clone the repository:

   ```bash
   git clone https://github.com/kpeez/neuromorphopy.git
   cd neuromorphopy
   ```

2. Sync dependencies:

   ```bash
   uv sync
   # OR using just
   just install
   ```

## Usage

### 1. Create a Query File

Define your search criteria in a `query.yaml` (or `.json`) file:

```yaml
filters:
  species: ["mouse", "rat"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
sort:
  field: "brain_region"
  order: "ascending"
```

### 2. Run Commands

Use the `neuromorpho` command to explore, preview, and download.

**Explore Fields:**
See what fields and values are available for filtering.

```bash
# List all filterable fields
neuromorpho fields

# List valid values for a specific field
neuromorpho fields species
```

**Preview Download:**
Check how many neurons match your query without downloading files.

```bash
neuromorpho preview query.yaml
```

**Download Data:**
Download the SWC morphology files and metadata.

```bash
# Download to default ./neurons directory
neuromorpho download query.yaml

# Download to a specific directory with higher concurrency
neuromorpho download query.yaml --output-dir ./data --concurrent 50

# Group downloaded files by species and brain region
neuromorpho download query.yaml --group-by species,brain_region
```

## Documentation

For more detailed usage and API reference, see our [documentation](docs/getting_started.md).
