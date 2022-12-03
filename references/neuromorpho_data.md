# Accessing NeuroMorpho database

- Trying to use: <https://github.com/NeuroBox3D/neuromorpho>
- Keep getting SSL cert errors :(

Steps needed to download a .swc file from neuromorpho.org

 1. download the neuron info (e.g., by index) and save as json file
 2. look up the `neuron_name` from the neuron’s json file
     - e.g., for neuron index=1: <https://neuromorpho.org/api/neuron/id/1>, `neuron_id = "cnic_001"`
 3. load the neuromorpho page for that neuron: <https://neuromorpho.org/neuron_info.jsp?neuron_name=cnic_001>
 4. find the URL for Morphology File (Standardized) from the page in (3)
     - e.g., `<a href="dableFiles/wearne_hof/CNG%20version/cnic_001.CNG.swc">Morphology File (Standardized)</a>`
     - neuromorpho uses regex for this
     - append the href to neuromorpho website: <http://neuromorpho.org/dableFiles/wearne_hof/CNG%20version/cnic_001.CNG.swc>
 5. open the URL from 4c and write to .swc file

## Resources

- Accessing the NeuroMorpho API using requests by default raises SSLCertification errors.
  - Even setting `verify=False` which should turn off SSL verification raises a DH_KEY_TOO_SMALL error. So to bypass that I used the cipher set solution [from this stack post](https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small).

## Analysis ideas

## Expt 1

**Goal: Classify neocortical pyramidal cells vs thalamic cells**
Neuromorpho query:

## Expt 2

**Goal: Classify neocortical pyramidal cells vs inhibitory neurons (basket cells, stellate cells)**
Neuromorpho query:
