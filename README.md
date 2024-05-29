# Python API to extract SensingClues data 

## Introduction

[SensingClues](https://sensingclues.org/) allows you to record, monitor and analyze wildlife observations to support nature conservation initiatives.
The package ``sensingcluespy`` allows Python-users to connect to SensingClues' database and download
data logged using the Cluey-app. This includes wildlife observations and tracks, custom map layers,
and the wildlife ontology used by SensingClues. **Note:** you need credentials for the 
SensingClues [Cluey](https://sensingclues.org/cluey)-app to connect to the database.

See the installation and usage instructions below. For more details, see 
[API-documentation](https://sensingcluespy.readthedocs.io/en/latest/#).

## Installation

There are various methods to install `sensingcluespy`. For any method, we recommend using a virtual environment when installing the library, such as pyenv or virtualenv.

The simplest method is to install ``sensingcluespy`` directly from pypi::
```python
pip install sensingcluespy
```

To download the source code and install the library:
```python
git clone https://github.com/SensingClues/sensingcluespy.git
cd </parent_location_of_the_library/sensingcluespy/>
pip install .
pip install -r requirements.txt
```

Further, we recommend using `jupytext` when working with Jupyter notebooks. Install it like so:
```python
pip install jupytext
```

Finally, you should create a personal account for SensingClues using the Cluey Data Collector app, which can be 
downloaded from the Google Playstore (not supported for iOS currently). 
Also see [here](https://sensingclues.org/portal).

Note: if you are developing new functionality, please also do:
```python
pip install -r requirements_dev.txt
pre-commit install
```

## Usage

The best way to get acquainted with the functionality availability in `sensingcluespy` is 
to check the notebook `notebooks/sensingclues_tutorial.py.`

Methods which are currently implemented are:
- `login` and `logout`: Connect to the database.
- `get_groups`: Obtain overview of groups you have access to.
- `get_observations`: Extract observations. 
- `get_tracks`: Extract track data.
- `add_geojson_to_tracks`: Add geospatial information to track data.
- `get_all_layers`: Obtain overview of all layers you have access to.
- `get_layer_features`: Extract detailed information on a layer.
- `get_hierarchy`: Get full hierarchy (ontology) used in database.
- helper functions related to the hierarchy/ontology, such as `get_label_for_id` and
`get_children_for_label`
- `get_concept_counts`: Get number of occurrences for a specific concept in the ontology.

The data can be filtered on for instance dates, coordinates and specific elements in the ontology.
See the detailed [API-documentation](https://sensingcluespy.readthedocs.io/en/latest/#) 
of each function to check which filters are available. 
