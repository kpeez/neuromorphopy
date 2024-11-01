# Data Formats

`neuromorphopy` works with two primary data formats:

## SWC Files

The [SWC format](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html) is the standard format used by NeuroMorpho.org for storing neuron morphologies. Each neuron is represented as a series of connected points in 3D space.

### File Structure

Each non-comment line in an SWC file contains 7 fields:

```plaintext

n T x y z R P
```

Where:

- n: Point identifier (integer)
- T: Type (integer)
  - 1: Soma
  - 2: Axon
  - 3: Basal dendrite
  - 4: Apical dendrite
  - 5+: Custom
- x, y, z: 3D coordinates (micrometers)
- R: Radius at that point (micrometers)
- P: Parent point (-1 for root)

Example:

```plaintext
# Example SWC file
1 1  0.0000  0.0000  0.0000  6.8127 -1
2 2 -7.1877 -4.2836  3.0000  1.2300  1
3 2 -11.2377 -7.2236  3.0600  1.2300  2
4 2 -11.2377 -7.2236  3.0600  0.5550  3
```

## Metadata CSV

When downloading neurons, neuromorphopy automatically saves metadata in CSV format. This includes:

- neuron_name: Unique identifier
- brain_region: Anatomical location
- cell_type: Morphological classification
- species: Source organism
- archive: Original data source
- reconstruction_software: Tool used for reconstruction

The metadata fields match the query fields available through the NeuroMorpho API.
