# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Extract wildlife observation data with SensingClues
#
# [SensingClues](https://sensingclues.org/) allows you to record, monitor and analyze wildlife observations to support nature conservation initiatives. This notebook shows the following:
# - **Basic**: the main SensingClues-functionality of **extracting observation and track data**. 
# - **Advanced**: this section includes the usage of a hierarchy of available concepts (e.g. animal species or type of activity), which enhances reporting and analysis of the observation data. Further, we show how to collect and visualize layer data from SensingClues.
#
# You can adapt this notebook to extract your own recordings. For more detail on what you can configure as a user, see the API-documentation of the `sensingclues`-package.
#
# ### Before you start
#
# To run this notebook, you should:
# - create a personal account at SensingClues using the Cluey Data Collector app, which can be downloaded from the Google Playstore (not supported for iOS currently). Also see [here](https://sensingclues.org/portal).
# - install the `sensingclues`-package in a virtual python environment (`pip install -e .` from the main directory of the repository).
# - install the requirements in requirements.txt (if not already installed automatically in the previous step).
# - create a file '.env' in the root of the wildcat-api-python-repository, containing your SensingClues credentials. These will be read in this notebook to log in. The file should look like this:
# ```
# # SensingClues credentials
# USERNAME=your_username
# PASSWORD=your_password
# ```

# ## Configuration

import os

from dotenv import load_dotenv

from sensingclues import sclogging
from sensingclues.api_calls import SensingClues
from sensingclues.src import helper_functions as helpers

logger = sclogging.get_sc_logger()
sclogging.set_sc_log_level("DEBUG")

load_dotenv()

# %load_ext autoreload
# %autoreload 2

# N.B. you can place your credentials here as well, but this is not recommended.
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


# ## Connect to SensingClues

sensing_clues = SensingClues(username, password)

# +
# you should have logged in automatically by calling the class.
# if not, you can call the login-method separately.
# status = sensing_clues.login(username, password)

# +
# It is not necessary to log out, but you can do so by calling:
# sensing_clues.logout()
# -

# ## Check available data
#
# By default, you have access to several groups of data, such as a demo dataset and a large dataset offered by [Global Forest Watch](https://www.globalforestwatch.org).

info = sensing_clues.get_groups()
info

# specify the group(s) to extract data from
groups = [
    "focus-project-1234",
]

# ## Basic functionality
#
# - Get observation data
# - Get track data

# ### Get observations
#
# You can filter the extracted observations in multiple ways, such as data, coordinates (bounding box) and concepts. For full detail on the options, see the documentation of the API. Some key features are shown here:
#
# - **Date and time**: set `date_from` and/or `date_until` (in format %Y-%m-%d, assumes UTC).
# - **Coordinates**: set `coord`, e.g. {"north": 32, "east": 20, "south": 31, "west": 17}.
# - **Concepts**: set `concepts` to include, e.g. 'animal'. *See example shown later in this notebook*.
#
# #### Notes
# - Each observation has a unique `entityId` and may have multiple concepts (labels) associated with it,
#  in which case the number of records in the observations-dataframe is larger than
#  the number of observations mentioned by the logger.
# - Reading all data in a group can take minutes or longer, depending on the size of the dataset. If you want to do a quick test, you can limit the number of pages to read by setting `page_nbr_sample`. 

# a quick test can be done like so
obs_sample = sensing_clues.get_observations(groups=groups, page_nbr_sample=2)

# see the API-documentation for a full description of filter possibilities
# to filter on concepts, see example shown later in this notebook.
observations = sensing_clues.get_observations(
    groups=groups,
    date_until="2018-07-01",
    coord={"north": 32, "east": 20, "south": 31.5, "west": 10}
)

observations.head()

# ### Get tracks
#
# You can filter the extracted observations in multiple ways, such as data, coordinates (bounding box) and concepts, similar to `get_observations`. 

tracks = sensing_clues.get_tracks(
    groups=groups,
    date_until="2018-07-01",
    coord={"north": 32, "east": 20, "south": 31.5, "west": 10}
)

tracks.head()

# #### Add geosjon-data to tracks
#
# If available, you can add geojson-data (including geometries) to the tracks.

tracks_geo = sensing_clues.add_geojson_to_tracks(tracks)

# ## Advanced functionality

# ### Get all available concepts and their hierarchy
#
# SensingClues offers hierarchies containing the available concepts (e.g. animals). As shown later in this notebook, you can use this information to subsequently query:
# - the details for a specific concept
# - check the occurrence of each concept in the group(s) of observations you have access to.

hierarchy = sensing_clues.get_hierarchy(scope="SCCSS")
hierarchy.info()

# ### Get details for specific concepts in the hierarchy
#
# You can get information on children or the parents of a concept in the hierarchy by filtering on its label or id. Use the available helper functions to do so. For example, you could do the following for the concept of a "Kite" (oid = "https://sensingclues.poolparty.biz/SCCSSOntology/222"):
#
# ```
# oid = "https://sensingclues.poolparty.biz/SCCSSOntology/222"
# helpers.get_children_for_id(hierarchy, oid)
# helpers.get_parent_for_id(hierarchy, oid)
# helpers.get_label_for_id(hierarchy, oid)
# ```
#
# or, if filtering on the label itself:
#
# ```
# label = 'Kite'
# helpers.get_children_for_label(hierarchy, label)
# helpers.get_parent_for_label(hierarchy, label)
# helpers.get_id_for_label(hierarchy, label)
# ```
#
# N.B. Alternatively, you could directly filter the `hierarchy`-dataframe yourself of course.

# #### Tell me, what animal belongs to this concept id?

oid = "https://sensingclues.poolparty.biz/SCCSSOntology/222"
helpers.get_label_for_id(hierarchy, oid)

# #### Does this Kite have any children?

label = "Kite"
children_label = helpers.get_children_for_label(hierarchy, label)
children_label


# #### What are the details for these children?

hierarchy.loc[hierarchy["id"].isin(children_label)]

# ### Filter observations on concept
#
# Here we show an example of filtering the data on these concepts.
#
# **Instructions:**
# - Set `concepts` to include, e.g. 'animal', specified as a Pool Party URL, e.g. "https://sensingclues.poolparty.biz/SCCSSOntology/186".
# - Note that you can infer the URL's available for a certain common name by using the helper function `helpers.get_label_for_id(hierarchy, oid)`, as shown above.
# - Further, if you want to exclude subconcepts, i.e. keep observations with the label 'animal' but exclude observations with the label 'elephant', set `include_subconcepts=False`.
#

concept_animal = [
    "https://sensingclues.poolparty.biz/SCCSSOntology/308", # Impala
    "https://sensingclues.poolparty.biz/SCCSSOntology/319", # Giraffe    
    
    # or infer the id using a label, for instance:
    # helpers.get_id_for_label(hierarchy, "Animal sighting"),
]
observations = sensing_clues.get_observations(
    groups=groups,
    date_until="2018-07-01",
    concepts=concept_animal,
    coord={"north": 32, "east": 20, "south": 31.5, "west": 10}
)

observations.head()

# ### Count concepts related to observations
#
# Get the number of observations per concept in the ontology (hierarchy).
#
# You can filter on for instance:
# - `date_from` and `date_until`.
# - A list of child concepts, e.g. by extracting children for the label "Animal sighting" from hierarchy (see example below).

date_from = "2010-01-01"
date_until = "2024-01-01"
label = "Animal sighting"
children_label = helpers.get_children_for_label(hierarchy, label)
concept_counts = sensing_clues.get_concept_counts(
    groups, date_from=date_from, date_until=date_until, concepts=children_label
)
concept_counts.head()

# #### Example: visualize concept counts
#
# To make the visualization intelligible, you can add information on labels from the `hierarchy`-dataframe.
#
# To do so, first install matplotlib.

# +
# # !pip install matplotlib
# -

import matplotlib.pyplot as plt
plt.style.use("ggplot")

min_freq = 10
if not concept_counts.empty:
    concept_freq = concept_counts.merge(
        hierarchy, left_on="_value", right_on="id", how="left"
    )
    concept_freq["label"] = concept_freq["label"].fillna(concept_freq["_value"])
    concept_freq = concept_freq.set_index("label")["frequency"].sort_values(
        ascending=True
    )

    concept_freq.loc[concept_freq >= min_freq].plot(kind="barh")
    plt.title(
        f"Number of observations per concept in group(s)\n'{groups}' for label '{label}'\n"
        f"[{date_from} to {date_until} and minimum frequency {min_freq}]",
        fontsize=12,
    )
    plt.xlabel("Number of observations per concept label")
    plt.ylabel("Label of concept")

# ### Get layers

# check all available layers
layers = sensing_clues.get_all_layers()
layers

# ### Get details for an individual layer

layer = sensing_clues.get_layer_features(layer_name="test_multipolygon")

layer.head()

# #### Plot available geometries
#
# This requires installation of library to visualize geospatial data. Here, we use Folium.

# +
# # !pip install folium
# -

import folium

poly_map = folium.Map([51.9244, 4.4777], zoom_start=8, tiles="cartodbpositron")
for _, geometry in layer["geometry"].items():
    folium.GeoJson(geometry).add_to(poly_map)
folium.LatLngPopup().add_to(poly_map)
poly_map



