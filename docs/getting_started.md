# Getting Started

This guide will help you get up and running with `neuromorphopy` quickly.

## Installation

### Using pip

```bash
git clone https://github.com/kpeez/neuromorphopy.git
cd neuromorphopy
pip install -r requirements.txt
pip install -e .
```

### Development Installation

We recommend using [uv](https://github.com/astral-sh/uv) for development:

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/kpeez/neuromorphopy.git
cd neuromorphopy
uv venv
uv sync
```

## Basic Usage

### 1. Creating Queries

neuromorphopy provides multiple ways to create queries:

#### Using YAML/JSON Files

Create a query file:

```yaml
# query.yml
filters:
  species: ["mouse"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
sort:
  field: "brain_region"
  ascending: true
```

Load and use the query:

```python
from neuromorphopy import Query, search_and_download

query = Query.from_file("query.yml")
search_and_download(query, "./data")
```

#### Using Python API

```python
from neuromorphopy import Query

query = Query()
query.filter("species", ["mouse"])
    .filter("brain_region", ["neocortex"])
    .filter("cell_type", ["pyramidal"])
```

### 2. Exploring Available Fields

neuromorphopy provides tools to explore available query fields and values:

```python
from neuromorphopy import QueryFields

# Get all available fields
fields = QueryFields.get_fields()
print(fields)

# Get valid values for a specific field
brain_regions = QueryFields.get_values("brain_region")
print(brain_regions)

# Get complete reference
reference = QueryFields.describe()
print(reference)
```

### 3. Downloading Neurons

```python
from neuromorphopy import search_and_download

# Download neurons to specified directory
search_and_download(query, "./data")
```

The downloaded data will include:

- SWC files containing neuron morphologies
- Metadata CSV file with neuron information

### 4. Working with Downloaded Data

```python
import pandas as pd
from pathlib import Path

# Load metadata
metadata = pd.read_csv("./data/metadata.csv")

# Access SWC files
swc_files = list(Path("./data").glob("*.swc"))
```

## Next Steps

- Learn more about [building queries](user_guide/queries.md)
- Understand [downloading options](user_guide/downloading.md)
- Learn about [data formats](user_guide/data_formats.md)
- Review the [API reference](api_reference/client.md)
