# Getting Started

This guide will help you get up and running with `neuromorphopy` quickly. neuromorphopy helps you download and work with neuron morphology data from NeuroMorpho.org.

## Installation

Install using pip:

```bash
pip install neuromorphopy
```

## Basic Usage

### 1. Create a Query File

Create a text file named `query.yml` (or `.json`) with your search criteria:

```yaml
# query.yml
filters:
  species: ["mouse"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
sort: # optional
  field: "neuron_id"
  ascending: false
```

To download all neurons, use an empty filter set:

```yaml
# query_all.yml
filters: {}
```

### 2. Explore Search Fields

Before writing your query, you might want to see what fields and values are available. Use the `fields` command:

```bash
# List all available query fields
neuromorpho fields

# List valid values for a specific field (e.g., species)
neuromorpho fields species
```

### 3. Preview Download (Optional)

Before downloading potentially thousands of files, you can preview what your query will match using the `preview` command:

```bash
neuromorpho preview -q query.yml
```

This will validate your query file and show you:

- The total number of neurons matching your criteria.
- The target output directory and metadata filename.
- A few sample neuron names that would be downloaded.

This command does *not* download any neuron files or create log files.

### 4. Download Neurons

Once your query is ready, use the `download` command:

```bash
neuromorpho download -q query.yml -o ./my_neurons
```

This will:

- Validate your query file.
- Create the output directory (`./my_neurons` in this case, defaults to `./neurons`).
- Download all matching neuron SWC files into the `downloads/` subdirectory.
- Save a `metadata.csv` file in the output directory with information about the downloaded neurons.
- Create a log file in the output directory.

## Understanding the Downloaded Data

After downloading, you'll have:

1. A collection of .swc files (one per neuron) containing 3D neuron reconstructions
2. A metadata.csv file containing information about each downloaded neuron

## Common Options for `download`

```bash
# Specify output directory
neuromorpho download query.yml -o ./my_data

# Change metadata filename
neuromorpho download query.yml -m neuron_info.csv

# Download fewer neurons concurrently (default 20)
neuromorpho download query.yml -c 5

# Group downloads by species and brain region
neuromorpho download query.yml -g species,brain_region

# See more detailed progress output
neuromorpho download query.yml --verbose

# Suppress non-error output
neuromorpho download query.yml --quiet

# Disable writing log file
neuromorpho download query.yml --no-log
```

## Next Steps

- See [detailed CLI usage](cli/basic_usage.md) for more commands
- Learn about [advanced CLI features](cli/advanced_options.md)
- Understand [neuron data formats](user_guide/data_formats.md)
