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

### Dry Run Mode

Preview results without downloading:

```bash
neuromorpho search query.yml --dry-run
```

### Field Validation

Validate specific fields or values:

```bash
neuromorpho validate species "mouse"
neuromorpho validate brain_region "neocortex,hippocampus"
```

## Complex Queries

### Multiple Value Filters

Filter using multiple values:

```yaml
filters:
  species: ["mouse", "rat"]
  brain_region: ["neocortex", "hippocampus"]
  cell_type: ["pyramidal"]
```

### Combining Conditions

Use AND/OR operations:

```yaml
filters:
  AND:
    species: ["mouse"]
    cell_type: ["pyramidal"]
  OR:
    brain_region: ["neocortex", "hippocampus"]
```

## Progress and Logging

Control output verbosity:

```bash
neuromorpho search query.yml --verbose     # Detailed progress
neuromorpho search query.yml --quiet       # Minimal output
neuromorpho search query.yml --log-file downloads.log
```

## Error Handling

### Retry Configuration

Configure download retry behavior:

```bash
neuromorpho search query.yml --max-retries 5 --retry-delay 2
```

## Environment Variables

Configure default behavior using environment variables:
