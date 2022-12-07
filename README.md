# NeuroMorpho Data

[![codecov](https://codecov.io/gh/kpeez/neuromorpho-data/branch/main/graph/badge.svg)](https://codecov.io/gh/kpeez/neuromorpho-data)
[![Commit activity](https://img.shields.io/github/commit-activity/m/kpeez/neuromorpho-data)](https://img.shields.io/github/commit-activity/m/kpeez/neuromorpho-data)
[![License](https://img.shields.io/github/license/kpeez/neuromorpho-data)](https://img.shields.io/github/license/kpeez/neuromorpho-data)

Lightweight python package for downloading neuron morphologies from the [NeuroMorpho archives](https://neuromorpho.org/).

- **Github repository**: <https://github.com/kpeez/neuromorpho-data/>
- **Documentation** <https://kpeez.github.io/neuromorpho-data/>

## Installation

If using `poetry`, simply clone the repo and install

```bash
git clone https://github.com/kpeez/neuromorpho-data.git
cd neuromorpho-data
make install
```

## Usage

First, import and create a NeuroMorpho object:

```python
from neuromorpho_data.neuromorpho_api import NeuroMorpho

nm = NeuroMorpho()
```

To see a list of valid search fields you can access the `valid_field_names` attribute:

```python
nm.valid_field_names
```

### Getting neuron metadata from NeuroMorpho

To search the NeuroMorpho archives, construct a search query and run `get_neuron_metadata`.
For example, to get all of the mouse interneurons and pyramidal cells from hippocampus and neocortex, you would use the following:

```python
query = {
    "species": ["mouse"],
    "brain_region": ["neocortex", "hippocampus"],
    "cell_type": ["interneuron", "pyramidal"]
}
nm.get_neuron_metadata(query)
```

Note: this may take some time if you are request a large set of neurons.
For example, the above query takes ~3 mins to get info for ~26,000 neurons.

The results of the search can be viewed by accessing the `neuron_metadata` attribute:

```python
metadata = nm.neuron_metadata
```

### Downloading morphology data

Morphology data for a single neuron (in .swc format) can be obtained by passing in the `neuron_name`:

```python
nm.get_neuron_swc(neuron_name)
```

In order to get morphological reconstructions for every neuron in the query, use `get_neuron_swc`:

```python
nm.download_swc_data()
```

Note: this takes a ***long time*** for large groups of neurons. The above query takes ~7 hours to complete.

Once completed you can access a dictionary of {neuron_name: swc_data}:

```python
nm.swc_data
```

### Exporting data

The metadata from your query can be exported to a .csv file by providing an export path and a file name:

```python
nm.export_metadata(export_path, query_filename)
```

After downloading swc data you can export that as a .pkl file the same way:

```python
nm.export_swc_data(export_path, swc_filename)
```
