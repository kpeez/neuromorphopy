# Basic CLI Usage

`neuromorphopy` provides a simple command-line interface for downloading neuron morphologies.

## Commands

### Explore Search Fields (`fields`)

View available query fields:

```bash
neuromorpho fields
```

View valid values for a specific field:

```bash
neuromorpho fields brain_region
```

### Preview Download (`preview`)

Validate a query file and see what would be downloaded without actually downloading anything:

```bash
neuromorpho preview query.yml
```

Options:

- `-o, --output-dir`: Specify the target output directory (for preview display)
- `-m, --metadata-filename`: Specify the target metadata filename (for preview display)
- `--verbose`: Show detailed validation output
- `--quiet`: Suppress validation output except errors

### Download Neurons (`download`)

Download neurons matching your query:

```bash
neuromorpho download query.yml -o ./output
```

Options:

- `-o, --output-dir`: Output directory (default: ./neurons)
- `-m, --metadata-filename`: Metadata filename (default: metadata.csv)
- `-c, --concurrent`: Max concurrent downloads (default: 20)
- `--group-by`: Comma-separated fields to group downloads (e.g., `species,brain_region`)
- `--verbose`: Show detailed progress
- `--quiet`: Suppress all output except errors
- `--no-log`: Disable automatic log file creation

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
    neuromorpho download mouse_pyramidal.yml -o ./mouse_neurons
    ```

2. Find available brain regions:

    ```bash
    neuromorpho fields brain_region
    ```

3. Preview a download with custom metadata filename:

    ```bash
    neuromorpho preview query.yml -o ./data -m neuron_metadata.csv
    ```

4. Download with grouping:

    ```bash
    neuromorpho download query.yml -g species
    ```

## Next Steps

- Learn about [advanced query options](advanced_options.md)
- Explore the [Python API](../api/client.md) for programmatic usage
- Review [data formats](../user_guide/data_formats.md)
