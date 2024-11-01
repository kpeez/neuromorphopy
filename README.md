# neuromorphopy

[![License](https://img.shields.io/github/license/kpeez/neuromorphopy)](https://img.shields.io/github/license/kpeez/neuromorphopy)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://kpeez.github.io/neuromorphopy/)

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

The easiest way to install is using pip:

```bash
git clone https://github.com/kpeez/neuromorphopy.git
cd neuromorphopy
pip install -r requirements.txt
pip install -e .
```

### Development

For development work, we recommend using [uv](https://github.com/astral-sh/uv) for faster dependency resolution and better reproducibility:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/kpeez/neuromorphopy.git
cd neuromorphopy
uv venv
uv sync
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

Use the command line interface to search and download neurons:

```bash
neuromorpho search -q query.yml -o ./data
```

For advanced usage and programmatic API, see our [documentation](https://neuromorphopy.readthedocs.io/).
