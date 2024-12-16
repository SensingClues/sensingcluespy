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

# # SensingClues IO
#
# [SensingClues](https://sensingclues.org/) helps nature conservation professionals
# with data-driven solutions to protect, manage and nurture nature.
# The Cluey Data Collector app can be used to record wildlife sightings, human-wildlife conflicts,
# illegal activities, community work, and monitor the status of park assets such as water points, fences and roads.
#
# This notebook uses the SensingClues Python API ([GitHub](https://github.com/SensingClues/sensingcluespy)) to collect the data captured in Cluey. The notebook shows the following:
# 1. **Basic**: the main SensingClues-functionality of **extracting observation and track data**.
# 2. **Advanced**: this section includes the usage of a hierarchy of available concepts (e.g. animal species or type of activity), which enhances reporting and analysis of the observation data. Further, we show how to collect and visualize layer data from SensingClues.
#
# Here, we use a demo dataset. You can adapt this notebook to extract your own recordings. For more detail on what you can configure as a user, see the [API-documentation]https://sensingcluespy.readthedocs.io/en/latest/index.html) of the package.
#
# ### [Optional] Create your own user account
#
# For the purpose of this tutorial, we use a **read-only** user called "demo". If you want to continue using SensingClues for your own work (of course you want to! :-) ), then please do the following:
# - Create a personal account at SensingClues using the Cluey Data Collector app, which can be downloaded from the Google Playstore (not supported for iOS currently). Also see [here](https://sensingclues.org/portal).
# - Create a file '.env' in the root of the wildcat-api-python-repository, containing your SensingClues credentials. These will be read in this notebook to log in. The file should look like this:
# ```
# # SensingClues credentials
# USERNAME=your_username
# PASSWORD=your_password
# ```

# ## Setup

# ### SensingClues

# !pip install ecoscope &> /dev/null

# +
# Only run this if directly running from Ecoscope (or add it to Ecoscope-requirements)
# # !pip install sensingcluespy &> /dev/null

# +
import getpass
import os
import sys

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from sensingcluespy.ecoscope import SensingCluesEcoscope

import ecoscope

ecoscope.init()

# +
# N.B. We recommend to place your credentials in an environment file and read them like so:
# username = os.getenv("USERNAME")
# password = os.getenv("PASSWORD")

# However, for the purpose of this demo, we use a read-only demo user:
username = "demo"
password = "demo"
# -

# ### Google Drive Setup

USE_GOOGLE_DRIVE = False

if USE_GOOGLE_DRIVE:
    output_dir = "Ecoscope-Outputs"
    
    if "google.colab" in sys.modules:
        from google.colab import drive
    
        drive.mount("/content/drive/", force_remount=True)
        output_dir = os.path.join("/content/drive/MyDrive/", output_dir)
    
    os.makedirs(output_dir, exist_ok=True)

# ## Connect to SensingClues

sc_io = SensingCluesEcoscope(username, password)

# ## Check available data
#
# By default, you have access to several groups of data, such as a demo dataset and a large dataset offered by [Global Forest Watch](https://www.globalforestwatch.org).

sc_io.groups

# Specify the group(s) to extract data from
# For this tutorial, focus-project-1234 contains demo observations,
# while focus-project-3494596 contains demo tracks.
groups = [
    "focus-project-3494596",
    "focus-project-1234",
]

# ## GET `Event`

# Get all events
events = sc_io.get_events(groups=groups)

events.info()

# ### By `event_ids`
# Use this approach to download an individual `Event` if you know its id. Downloading from multiple ids at once is currently unsupported in ER.

sc_io.get_events(
    event_ids="O3494596-nff20c1dac0817042",  # Elephant sighting event
    groups=groups,
)

# # WORK IN PROGRESS FROM HERE

# ### By `event_type`
# Use this approach if you want to download events of a given event type (using the EventType ID from ER)

df_event_types = pd.DataFrame(sc_io.get_event_types())
mep_elephant_sighting_id = df_event_types[df_event_types["value"] == "mep_elephant_sighting"]["id"].values[0]
mep_elephant_sighting_id

er_io.get_events(
    event_type=[mep_elephant_sighting_id],  # MEP Elephant Sighting
    since=pd.Timestamp("2019-05-01").isoformat(),
    until=pd.Timestamp("2020-05-01").isoformat(),
).reset_index(drop=True)

# ### Unpack `event_details` column of `JSON` data into individual columns

df_event_types = pd.DataFrame(er_io.get_event_types())
mep_distance_survey_id = df_event_types[df_event_types["value"] == "mepdev_distance_count"]["id"].values[0]
mep_distance_survey_id

events_df = er_io.get_events(event_type=[mep_distance_survey_id])  # MEP Distance Survey Count
events_df.event_details

er_io._normalize_column(events_df, "event_details")
events_df

# ## POST `Event`
#
# First delete any existing events:

df_event_types = pd.DataFrame(er_io.get_event_types())
carcass_id = df_event_types[df_event_types["value"] == "carcass_rep"]["id"].values[0]
carcass_id

event_df = er_io.get_events(
    event_type=[carcass_id],  # Carcass
)
if not event_df.empty:
    for i, value in event_df.iterrows():
        er_io.delete_event(event_id=event_df.loc[i, "id"])

# Define events to be uploaded:

new_event = [
    {
        "event_details": {
            "carcassrep_ageofanimal": None,
            "carcassrep_ageofcarcass": None,
            "carcassrep_causeofdeath": None,
            "carcassrep_sex": None,
            "carcassrep_species": None,
            "carcassrep_trophystatus": None,
        },
        "event_type": "carcass_rep",
        "icon_id": "carcass_rep",
        "id": "e29f9078-ee0a-4f06-b685-92e9ff266e9b",
        "location": {"latitude": -27.12759, "longitude": -109.40804},
        "priority": 100,
        "state": "resolved",
        "time": pd.Timestamp("2022-03-15 15:44:00-0700"),
        "title": "Carcass",
    }
]

# Read events as dataframe:

new_event_df = pd.DataFrame.from_dict(new_event)
new_event_df

# Upload:

try:
    er_io.post_event(events=new_event_df.iloc[[0]])
except ERClientException as e:
    print(e)

# ## PATCH `Event`
#
# Define updated values

updated_event = pd.DataFrame(
    [
        {
            "event_details": {
                "carcassrep_ageofanimal": "adult",
                "carcassrep_ageofcarcass": "less_than_a_day",
                "carcassrep_causeofdeath": "unnaturalshot",
                "carcassrep_sex": "female",
                "carcassrep_species": "elephant",
                "carcassrep_trophystatus": "removed",
            }
        }
    ]
)

# Get and display current values

# +
event_df = er_io.get_events(
    event_type=["b0d66402-34cb-4e9a-9715-2ac4eeebb574"],  # Carcass
)

event_df.loc[0, "event_details"]
# -

# Patch and confirm values have been updated

id_to_patch = event_df.loc[0, "id"]
er_io.patch_event(event_id=id_to_patch, events=updated_event).loc[0, "event_details"]

# ## GET `Subjects`

# ### by `id`

df_subjects = er_io.get_subjects()
habiba_id = df_subjects[df_subjects["name"] == "Habiba"]["id"].values[0]
habiba_id

er_io.get_subjects(id=habiba_id)  # Habiba

# ### By `SubjectGroup` `group_name`

er_io.get_subjects(group_name="Elephants")

# ## GET `Observations`
#
# The output is an Ecoscope `Relocations` dataframe that has a core set of columns: `groupby_col`, `fixtime`, `junk_status`.
#
# All other columns are prepended by `extra__`. The `groupby_col` will be the `subject_id` and the index of the dataframe is the observation indices.
#
# Classic ER `Observation` format can be returned by passing in parameter `relocations=False`.
#
# Filter observation by setting `filter` to one of: None, 0, 1, 2 or 3
# - None returns everything
# - 0 filters out everything but observations with exclusion flag 0 (Pass back clean data)
# - 1 filters out everything but observations with exclusion flag 1 (Pass back manually filtered data)
# - 2 filters out everything but observations with exclusion flag 2 (Ppass back automatically filtered data)
# - 3 filters out everything but observations with exclusion flag 2 or 1 (Pass back both manual and automatic filtered data)

# ### By `SubjectGroup` `group_name`:

since = pd.Timestamp("2008-01-01").isoformat()
until = pd.Timestamp("2020-01-01").isoformat()

relocs = er_io.get_subjectgroup_observations(
    group_name="Elephants",
    filter=0,
    since=since,
    until=until,
    include_details=True,
    include_inactive=True,
    include_source_details=True,
    include_subject_details=True,
    include_subjectsource_details=True,
)
relocs

# ### By `subject_id`

df_subjects = er_io.get_subjects()
habiba_id = df_subjects[df_subjects["name"] == "Habiba"]["id"].values[0]
salif_keita_id = df_subjects[df_subjects["name"] == "Salif Keita"]["id"].values[0]
habiba_id, salif_keita_id

relocs = er_io.get_subject_observations(
    subject_ids=[
        habiba_id,  # Habiba
        salif_keita_id,  # Salif Keita
    ],
    since=since,
    until=until,
    filter=0,
    include_details=True,
    include_subject_details=True,
    include_source_details=True,
    include_subjectsource_details=True,
)
relocs

# ### By `source_id`

df_sources = er_io.get_sources()
habiba_source_id = df_sources[df_sources["manufacturer_id"] == "ST-Habiba"]["id"].values[0]
salif_keita_source_id = df_sources[df_sources["manufacturer_id"] == "ST-SalifKeita"]["id"].values[0]
habiba_source_id, salif_keita_source_id

# +
df_sources = er_io.get_sources()

relocs = er_io.get_source_observations(
    source_ids=[
        habiba_source_id,  # Habiba's Source
        salif_keita_source_id,  # Salif Keita's Source
    ],
    since=since,
    until=until,
    filter=0,
    include_details=True,
    include_source_details=True,
)
relocs
# -

# ## GET `Patrols`

df_patrol_types = er_io.get_patrol_types()
mep_distance_id = df_patrol_types[df_patrol_types["value"] == "MEP_Distance_Survey_Patrol"]["id"].values[0]
mep_distance_id

er_io.get_patrols(patrol_type=[mep_distance_id])  # MEP Distance Count Survey

# ## GET `Observations` for a `Patrol`

# +
patrol_df = er_io.get_patrols()

relocs = er_io.get_patrol_observations(
    patrol_df,
    include_patrol_details=True,
    include_source_details=True,
    include_subject_details=True,
    include_subjectsource_details=True,
)
relocs
# -

# ## GET `SPATIAL FEATURES`

# ### GET `SPATIAL FEATURE` from `spatial_feature_id`

spatial_feature = er_io.get_spatial_feature(spatial_feature_id="8868718f-0154-45bf-a74d-a66706ef958f")
spatial_feature

# ### GET `SPATIAL FEATURES` from `spatial_features_group_id`

spatial_features = er_io.get_spatial_features_group(spatial_features_group_id="15698426-7e0f-41df-9bc3-495d87e2e097")
spatial_features

# ## GET `Users`

df = pd.DataFrame(er_io.get_users())
df

# ## POST `Observation`

# First delete any existing observations

# +
elephants = er_io.get_subjectgroup_observations(group_name="Elephants", since=pd.Timestamp("2022-01-01").isoformat())

if not elephants.empty:
    for i, value in elephants.iterrows():
        er_io.delete_observation(observation_id=elephants.loc[i, "extra__id"])
# -

# Create new observations from existing sources

df_sources = er_io.get_sources()
habiba_source_id = df_sources[df_sources["manufacturer_id"] == "ST-Habiba"]["id"].values[0]
salif_keita_source_id = df_sources[df_sources["manufacturer_id"] == "ST-SalifKeita"]["id"].values[0]
habiba_source_id, salif_keita_source_id

# +
observations = [
    {
        "fixtime": pd.Timestamp("2023-04-24 11:03:31").isoformat(),
        "geometry": Point(1.99, 2.99),
        "source_id": habiba_source_id,  # Habiba's source
    },
    {
        "fixtime": pd.Timestamp("2023-02-01 14:02:05").isoformat(),
        "geometry": Point(1.345, 2.3303),
        "source_id": habiba_source_id,  # Habiba's source
    },
    {
        "fixtime": pd.Timestamp("2023-03-21 06:03:27").isoformat(),
        "geometry": Point(3.4455, -3.4554),
        "source_id": salif_keita_source_id,  # Salif Keita's source
    },
]

gdf = gpd.GeoDataFrame.from_dict(observations)
gdf
# -

# Post observations

er_io.post_observations(observations=gdf, source_id_col="source_id", recorded_at_col="fixtime")

# ## POST `SubjectSource`

# +
df_subjects = er_io.get_subjects()
salif_keita_id = df_subjects[df_subjects["name"] == "Salif Keita"]["id"].values[0]

df_sources = er_io.get_sources()
salif_keita_source_id = df_sources[df_sources["manufacturer_id"] == "ST-SalifKeita"]["id"].values[0]

salif_keita_id, salif_keita_source_id
# -

er_io.post_subjectsource(
    salif_keita_id,  # Salif Keita subject ID
    source_id=salif_keita_source_id,  # Salif Keita's source
    lower_bound_assigned_range=pd.Timestamp.utcnow().isoformat(),
    upper_bound_assigned_range=(pd.Timestamp.utcnow() + pd.Timedelta(days=9000)).isoformat(),
    additional={},
)

# ## Export to File

# ### Create test data
#
# Skip this cell if you would like to provide your own data

relocs = er_io.get_subjectgroup_observations(
    group_name="Elephants",
    filter=0,
    since=since,
    until=until,
    include_details=True,
    include_inactive=True,
    include_source_details=True,
    include_subject_details=True,
    include_subjectsource_details=True,
)
relocs

# ### GeoPackage (.gpkg) 
# (GeoPackage does not support columns with type `list` so we `drop` them.)

# +
relocs.drop(
    columns=relocs.columns[relocs.applymap(lambda x: isinstance(x, list)).any()],
    errors="ignore",
    inplace=True,
)

relocs.to_file(os.path.join(output_dir, "observations.gpkg"), layer="observations")
# -

# ### CSV

relocs.to_csv(os.path.join(output_dir, "observations.csv"))

# ### Python Pickle (.pkl)

relocs.to_pickle(os.path.join(output_dir, "observations.pkl"))

# ### Apache Feather (.feather)

relocs.to_feather(os.path.join(output_dir, "observations.feather"))
