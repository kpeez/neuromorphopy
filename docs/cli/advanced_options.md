# Advanced CLI Options

## Concurrent Downloads

Control parallel downloads to optimize performance:

```bash
neuromorpho search query.yml -c 30  # Increase concurrent downloads
neuromorpho search query.yml -c 5   # Reduce for slower connections
```

## Custom Output Structure

### Metadata Organization

Customize metadata file location and name:

```bash
neuromorpho search query.yml -o ./neurons -m custom_metadata.csv
neuromorpho search query.yml -o ./neurons -m ./metadata/neurons.csv
```

### Output Directory Structure

Control how neurons are organized:

```bash
# Group by species
neuromorpho search query.yml -o ./neurons --group-by species

### Group by multiple fields

```bash
neuromorpho search query.yml -o ./neurons --group-by species,cell_type
```

## Query Validation

`neuromorphopy` provides comprehensive query validation to ensure your queries are correct before downloading.

### Validation Command

Validate a query file:

```bash
neuromorpho validate query.yml
```

The validator checks:

- File format and structure
- Query field names
- Field values
- Sort configuration (if present)

### Automatic Validation

Validation runs automatically when using the search command:

```bash
neuromorpho search query.yml  # Includes validation
neuromorpho search query.yml --verbose  # Shows detailed validation
```

### Dry Run Mode

Preview results without downloading:

```bash
neuromorpho search query.yml --dry-run
```

## Progress and Logging

Control output verbosity:

```bash
neuromorpho search query.yml --verbose     # Detailed progress
neuromorpho search query.yml --quiet       # Minimal output
neuromorpho search query.yml --no-log      # Disable automatic log file creation
```

Logs are automatically saved to the output directory with timestamps:

```bash
# Default: creates YYYY-MM-DD-HH_MM-queryname.log in output directory
neuromorpho search query.yml

# Disable logging
neuromorpho search query.yml --no-log
```
