# Getting Started

This guide will help you get up and running with `neuromorphopy` quickly. neuromorphopy helps you download and work with neuron morphology data from NeuroMorpho.org.

## Installation

Install using pip:

```bash
pip install neuromorphopy
```

## Basic Usage

### 1. Create a Query File

Create a text file named `query.yml` with your search criteria:

```yaml
# query.yml
filters:
  species: ["mouse"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
```

### 2. Validate Queries

Validate your query files before downloading:

```bash
neuromorpho validate query.yml
```

Note: Validation happens automatically when running the search command. Use the validate command to check queries without starting a download.

Options:

- `--quiet`: Suppress detailed validation output

### 2. Download Neurons

Open your terminal and run:

```bash
neuromorpho search query.yml -o ./my_neurons
```

This will:

- Create a folder called `my_neurons`
- Download matching neuron files (.swc format)
- Save a metadata.csv file with information about the neurons

### Using Dry Run Mode

Before downloading the neurons, you can preview the results using the dry run mode. This is useful to ensure your query is correct and to see what will be downloaded without actually downloading the files.

To use the dry run mode, run the following command:

```bash
neuromorpho search query.yml --dry-run
```

### 3. Find Available Search Options

To see what you can search for:

```bash
# List all brain regions
neuromorpho explore brain_region

# List all species
neuromorpho explore species

# List all cell types
neuromorpho explore cell_type
```

## Understanding the Downloaded Data

After downloading, you'll have:

1. A collection of .swc files (one per neuron) containing 3D neuron reconstructions
2. A metadata.csv file containing information about each downloaded neuron

## Common Options

```bash
# Download fewer neurons at once (for slower connections)
neuromorpho search query.yml -c 5

# See more detailed progress
neuromorpho search query.yml --verbose

# Preview what will be downloaded
neuromorpho search query.yml --dry-run
```

## Next Steps

- See [detailed CLI usage](cli/basic_usage.md) for more commands
- Learn about [advanced CLI features](cli/advanced_options.md)
- Understand [neuron data formats](user_guide/data_formats.md)
