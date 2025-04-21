# neuromorphopy

[![License](https://img.shields.io/github/license/kpeez/neuromorphopy)](https://img.shields.io/github/license/kpeez/neuromorphopy)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://neuromorphopy.readthedocs.io/)

Lightweight python package for downloading neuron morphologies from the [NeuroMorpho archives](https://neuromorpho.org/).

- **Github repository**: <https://github.com/kpeez/neuromorphopy/>

## Features

- Simple and intuitive API for searching NeuroMorpho.org
- Efficient concurrent downloads of neuron morphologies
- Flexible query system with validation
- Automatic metadata handling
- Support for both synchronous and asynchronous operations

## Requirements

- Python >= 3.11

## Installation

**Using `uv` (Recommended):**

The easiest way to install `neuromorphopy` as a standalone CLI tool is with [`uv`](https://github.com/astral-sh/uv):

```bash
# install the latest release
uv tool install neuromorphopy
# or install the latest development version from GitHub
uv tool install git+https://github.com/kpeez/neuromorphopy.git
```

**Using `pip`:**

Alternatively, you can install `neuromorphopy` into your project environment using `pip`:

```bash
# install the latest release
pip install neuromorphopy
# or install the latest development version directly from GitHub
pip install git+https://github.com/kpeez/neuromorphopy.git
```

## Usage

Create a query file (YAML or JSON) to specify what neurons you want:

```yaml
# query.yml
filters:
  species: ["mouse"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
sort: # sorting is optional
  field: "brain_region"
  ascending: true
```

To download all neurons, you can use an empty query:

```yaml
# query.yml
filters: {}
```

Use the command line interface to explore available fields, preview a query, or download neurons:

```bash
# Explore available query fields and values
neuromorpho fields
neuromorpho fields species

# Preview what a query would download
neuromorpho preview -q query.yml

# Download neurons matching the query
neuromorpho download -q query.yml -o ./data
```

For more detailed usage, see our [documentation](docs/getting_started.md).
