---
title: Home
---

{! README.md !}

## OLD BS

[![License](https://img.shields.io/github/license/kpeez/neuromorphopy)](https://img.shields.io/github/license/kpeez/neuromorphopy)

A lightweight Python package for downloading neuron morphologies from the [NeuroMorpho archives](https://neuromorpho.org/).

## Features

- Simple and intuitive API for searching NeuroMorpho.org
- Efficient concurrent downloads of neuron morphologies
- Flexible query system with validation
- Automatic metadata handling
- Support for both synchronous and asynchronous operations

## Quick Start

After installing neuromorphopy, you can search and download neuron morphologies by using a query file (YAML or JSON):
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

```python
from neuromorphopy import Query, search_and_download

# Create query from file and download neurons
query = Query.from_file("query.yml")
search_and_download(query, "./data")
```
