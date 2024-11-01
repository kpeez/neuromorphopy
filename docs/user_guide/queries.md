# Building Queries

`neuromorphopy` provides flexible ways to build and validate queries for searching the NeuroMorpho database. This guide covers all query-building approaches and advanced features.

## Query Structure

A query consists of two main components:

1. Filters: Define what neurons to search for
2. Sorting: Optional specification for result ordering

## Creating Queries

### From YAML/JSON Files

The simplest way to create a query is using a YAML or JSON file:

```yaml
# query.yml
filters:
  species: ["mouse"]
  brain_region: ["neocortex"]
  cell_type: ["pyramidal"]
sort:  # optional
  field: "brain_region"
  ascending: true
```

Load the query using:

```python
from neuromorphopy import Query

query = Query.from_file("query.yml")
```

### Using the Python API

You can build queries programmatically using method chaining:

```python
from neuromorphopy import Query

query = (Query()
         .filter("species", ["mouse"])
         .filter("brain_region", ["neocortex"])
         .filter("cell_type", ["pyramidal"])
         .sort("brain_region", ascending=True))
```

## Field Validation

`neuromorphopy` automatically validates all fields and values against the NeuroMorpho API. The `QueryFields` class provides utilities for exploring available options:

```python
from neuromorphopy import QueryFields

# Get all available fields
fields = QueryFields.get_fields()
print(fields)

# Get valid values for a specific field
brain_regions = QueryFields.get_values("brain_region")
print(brain_regions)

# Get complete reference of all fields and their values
reference = QueryFields.describe()
```

Invalid fields or values will raise a ValueError with helpful messages:

```python
# This will raise an error with valid options
query.filter("invalid_field", ["invalid_value"])
```

## Sorting Results

You can sort query results by any valid field:

```python
query = Query()
query.filter("species", ["mouse"]) \
     .sort("brain_region", ascending=True)  # ascending is optional, defaults to True
```

## Query Composition

Queries can be built incrementally:

```python
# Start with basic filters
query = Query()
query.filter("species", ["mouse"])

# Add more filters based on conditions
if include_cortex:
    query.filter("brain_region", ["neocortex"])

if cell_type:
    query.filter("cell_type", [cell_type])
```

## Field Reference

Common fields include:

- species
- brain_region
- cell_type
- archive
- domain
- experiment_condition

For a complete list of fields and their valid values:

```python
from pprint import pprint
from neuromorphopy import QueryFields

# Get all available fields and their values
reference = QueryFields.describe()
pprint(reference)
```

## Best Practices

1. Use YAML/JSON files for static queries
2. Use programmatic building for dynamic queries
3. Always check available fields and values using QueryFields
4. Handle validation errors appropriately
5. Consider sorting for consistent results
