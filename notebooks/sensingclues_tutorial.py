# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Extract wildlife observation data with SensingClues
#
# [SensingClues](https://sensingclues.org/) allows you to record, monitor and analyze wildlife observations to support nature conservation initiatives. This notebook shows the following:
#
# - **Core**: the main SensingClues-functionality of
#     1. Extracting observation data
#     2. Extracting track data
# - **Advanced**: additional functionality including
#     1. A hierarchy of available concepts (e.g. animal species or type of (illegal) activity), which enhances reporting and analysis of the observation data.
#     2. Extraction and visualization of layer data from SensingClues.
#
# You can adapt this notebook to extract your own observation data. For more detail on what you can configure as a user, see the API-documentation of the `sensingcluespy`-package [here](https://sensingcluespy.readthedocs.io/en/latest/).
#
# ### Before you start
#
# To run this notebook, you should:
# - Install the `sensingcluespy`-package in a virtual python environment (`pip install -e .` from the main directory of the repository).
# - Install the requirements in requirements.txt (if not already installed automatically in the previous step). This includes the plotting libraries `matplotlib` and `folium` used in this notebook.
#
# #### [Optional] Create your own user account
#
# For the purpose of this tutorial, we use a **read-only** user called "demo". If you want to continue using SensingClues for your own work (of course you want to! :-) ), then please do the following:
# - Create a personal account at SensingClues using the Cluey Data Collector app, which can be downloaded from the Google Playstore (not supported for iOS currently). Also see [here](https://sensingclues.org/portal).
# - Create a file '.env' in the root of the wildcat-api-python-repository, containing your SensingClues credentials. These will be read in this notebook to log in. The file should look like this:
# ```
# # SensingClues credentials
# USERNAME=your_username
# PASSWORD=your_password
# ```

# ## Configuration

# +
# N.B. While sensingcluespy does not require you to install visualization packages, this tutorial does.
# To run this tutorial in full, please install matplotlib and folium (as contained in requirements.txt).
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

from sensingcluespy import sclogging
from sensingcluespy.api_calls import SensingClues
from sensingcluespy.src import helper_functions as helpers
from sensingcluespy.src import visualization as viz
# -

plt.style.use("ggplot")

logger = sclogging.get_sc_logger()
sclogging.set_sc_log_level("INFO")

load_dotenv()

# %load_ext autoreload
# %autoreload 2

# +
# N.B. We recommend to place your credentials in an environment file and read them like so:
# username = os.getenv("USERNAME")
# password = os.getenv("PASSWORD")

# However, for the purpose of this demo, we use a read-only demo user:
username = "demo"
password = "demo"
# -


# ## Connect to SensingClues

sensing_clues = SensingClues(username, password)

# ## Check available data
#
# By default, you have access to several groups of data, such as a demo dataset and a large dataset offered by [Global Forest Watch](https://www.globalforestwatch.org).

info = sensing_clues.get_groups()
info

# Specify the group(s) to extract data from
# For this tutorial, focus-project-1234 contains demo observations,
# while focus-project-3494596 contains demo tracks.
groups = [
    "focus-project-3494596",
    "focus-project-1234",
]

# ## Core functionality
#
# Time to collect and plot some observation and track data!

# ### Get observations
#
# You can filter the extracted observations in multiple ways, such as timestamps, coordinates (bounding box) and concepts. Some key features are shown here:
#
# - **Date and time**: set `date_from` and/or `date_until` (in format %Y-%m-%d, assumes UTC).
# - **Coordinates**: set `coord`, e.g. {"north": 32, "east": 20, "south": 31, "west": 17}.
# - **Concepts**: set `concepts` to include, e.g. 'animal'. *See detailed example later in this notebook*.
#
# For full detail on the options, see the documentation of the API [here](https://sensingcluespy.readthedocs.io/en/latest/).
#
# #### Usage notes
# - Reading all data in a group can take minutes or longer, depending on the size of the dataset. If you want to do a quick test, you can limit the number of pages to read by setting `page_nbr_sample`.
# - Each observation has a unique `entityId` and may have multiple concepts (labels) associated with it, in which case the number of records in the observations-dataframe is larger than the number of observations mentioned by the logger.

# A quick check of the number of available records
obs_sample = sensing_clues.get_observations(groups=groups, page_nbr_sample=1)

observations = sensing_clues.get_observations(
    groups=groups,
    date_from="2024-07-01",
    coord={"north": -17, "east": 30, "south": -19, "west": 20}
)

# #### Visualize these observations
#
# The standard plotting-function `plot_observation` shows a separate layer for all observation types (typically ['community_work', 'animal', 'community', 'poi', 'hwc'], where 'poi' = 'point of interest' and 'hwc' = 'human-wildlife-conflict').

viz.plot_observations(
    observations, 
    show_heatmap="hwc_animal", 
    padding=(25, 25)
)

# You can explore the observations per observationType like so:
observation_type = "animal"
# observation_type = "hwc"
observations.loc[observations["observationType"] == observation_type, "conceptLabel"].value_counts()

# ### Get tracks
#
# You can filter the extracted observations in multiple ways, such as data, coordinates (bounding box) and concepts, similar to `get_observations`. 

tracks = sensing_clues.get_tracks(
    groups=groups,
    # date_from="2024-07-01",
    # coord={"north": -17, "east": 30, "south": -19, "west": 20}
)

tracks.head()

# #### Visualize tracks
#
# If available, you can add geojson-data (including geometries) to the tracks and subsequently visualize the tracks.

tracks_geo = sensing_clues.add_geojson_to_tracks(tracks)

track_map = viz.plot_tracks(tracks_geo["geometry"])
track_map

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

# #### Does this Kite have any child concepts?

label = "Kite"
children_label = helpers.get_children_for_label(hierarchy, label)
children_label


# #### What are the details for these children?

hierarchy.loc[hierarchy["id"].isin(children_label)]

# ### Filter observations on concept
#
# Here we show an example of filtering the data on concepts. The example filters on the concepts of Impala and Giraffe.
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
concept_observations = sensing_clues.get_observations(
    groups=groups,
    concepts=concept_animal,
    # date_from="2024-07-01",
    # coord={"north": -17, "east": 30, "south": -19, "west": 20}
)

concept_observations.head()

# ### Count concepts related to observations
#
# Get the number of observations per concept in the ontology (hierarchy).
#
# You can filter on for instance:
# - `date_from` and `date_until`.
# - A list of child concepts, e.g. by extracting children for the label "Animal sighting" from hierarchy (see example below).

date_from = "2010-01-01"
date_until = "2024-08-01"
label = "Animal sighting"
children_label = helpers.get_children_for_label(hierarchy, label)
concept_counts = sensing_clues.get_concept_counts(
    groups, date_from=date_from, date_until=date_until, concepts=children_label
)
concept_counts.head()

# #### Example: visualize concept counts
#
# To make the visualization intelligible, you can add information on labels from the `hierarchy`-dataframe.

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

# ### Visualize an individual layer
#
# Get features for an individual and visualize it.

layer = sensing_clues.get_layer_features(layer_name="Demo_countries")
viz.plot_layer(layer)

# ### Miscellaneous

# +
# You should have logged in automatically by calling the class.
# If not, you can call the login-method separately.
# status = sensing_clues.login(username, password)

# +
# It is not necessary to log out, but you can do so by calling:
# sensing_clues.logout()
