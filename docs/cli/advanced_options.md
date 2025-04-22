# Advanced CLI Options

## Concurrent Downloads

Control parallel downloads using the `-c` or `--concurrent` option with the `download` command:

```bash
neuromorpho download query.yaml -c 30  # Increase concurrent downloads
neuromorpho download query.yaml -c 5   # Reduce for slower connections
```

## Custom Output Structure

### Metadata Organization

Customize metadata file location and name using the `-m` or `--metadata-filename` option with the `download` command:

```bash
neuromorpho download query.yaml -o ./neurons -m custom_metadata.csv
# Note: Paths for metadata are relative to the output directory (-o)
# The following will save metadata to ./neurons/metadata/neurons.csv
neuromorpho download query.yaml -o ./neurons -m ./metadata/neurons.csv
```

### Output Directory Structure (`--group-by`)

Control how downloaded neuron files are organized within the `downloads/` subdirectory using the `--group-by` option with the `download` command. Provide a comma-separated list of metadata fields.

```bash
# Group by species (e.g., ./neurons/downloads/mouse/...)
neuromorpho download query.yaml -o ./neurons --group-by species

# Group by multiple fields (e.g., ./neurons/downloads/mouse/pyramidal/...)
neuromorpho download query.yaml -o ./neurons --group-by species,cell_type
```

## Query Validation

Validation runs automatically when using the `preview` or `download` commands. If the query file is invalid, the command will exit with an error.

```bash
neuromorpho preview query.yaml --verbose  # Shows detailed validation during preview
neuromorpho download query.yaml --verbose # Shows detailed validation before download
```

## Progress and Logging

Control output verbosity during downloads:

```bash
neuromorpho download query.yaml --verbose     # Detailed progress
neuromorpho download query.yaml --quiet       # Minimal output (errors only)
neuromorpho download query.yaml --no-log      # Disable automatic log file creation
```

Logs are automatically saved to the main output directory (not the `downloads` subdirectory) with timestamps when running `download`:

```bash
# Default: creates YYYY-MM-DD-HH_MM-queryname.log in output directory
neuromorpho download query.yaml

# Disable logging
neuromorpho download query.yaml --no-log
```
