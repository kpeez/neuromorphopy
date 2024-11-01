# Basic CLI Usage

`neuromorphopy` provides a simple command-line interface for downloading neuron morphologies.

## Commands

### Search and Download

Download neurons matching your query:

```bash
neuromorpho search query.yml -o ./output
```

Options:

- `-o, --output-dir`: Output directory (default: ./neurons)
- `-m, --metadata-filename`: Metadata filename (default: metadata.csv)
- `-c, --concurrent`: Max concurrent downloads (default: 20)
- `--verbose`: Show detailed progress
- `--quiet`: Suppress all output except errors
- `--no-log`: Disable automatic log file creation

### Validate Queries

Validate your query files before downloading:

```bash
neuromorpho validate query.yml
```

Note: Validation happens automatically when running the search command. Use the validate command to check queries without starting a download.

Options:

- `--quiet`: Suppress detailed validation output

### Explore Fields

View available query fields:

```bash
neuromorpho explore
```

View valid values for a field:

```bash
neuromorpho explore brain_region
```

## Query File Format

Create YAML files with your search criteria:

```yaml
filters:
  species: ["mouse"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
sort:  # optional
  field: "brain_region"
  ascending: true
```

## Examples

1. Download mouse pyramidal neurons:

    ```yaml
    # mouse_pyramidal.yml
    filters:
      species: ["mouse"]
      cell_type: ["pyramidal"]
    ```

    ```bash
    neuromorpho search mouse_pyramidal.yml -o ./mouse_neurons
    ```

2. Find available brain regions:

    ```bash
    neuromorpho explore brain_region
    ```

3. Download with custom metadata filename:

    ```bash
    neuromorpho search query.yml -o ./data -m neuron_metadata.csv
    ```

## Next Steps

- Learn about [advanced query options](advanced_options.md)
- Explore the [Python API](../api/client.md) for programmatic usage
- Review [data formats](../user_guide/data_formats.md)
