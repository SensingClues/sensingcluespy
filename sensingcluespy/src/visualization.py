"""Functions used for plotting of SensingClues-data"""

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from folium.plugins import HeatMap
from typing import Tuple


def plot_layer(
    layer: gpd.GeoDataFrame,
    geometry_col: str = "geometry",
    name_col: str = "NAME"
) -> folium.folium.Map:
    """Visualize layer on a map

    Parameters
    ----------
    layer : gpd.GeoDataFrame
        GeoDataFrame with details of a layer.
    geometry_col : str
        Name of the column containing the layer geometries.
    name_col : str
        Name the column containing the layer names.

    Returns
    -------
    poly_map : folium.folium.Map
        Map object.

    """
    poly_map = folium.Map(tiles="cartodbpositron")
    colors = plt.rcParams['axes.prop_cycle'].by_key()["color"]

    feature_groups = {}
    for i, geometry in layer[geometry_col].items():
        color_id = i % (len(colors) - 1)
        name = layer[name_col].iloc[i]
        feature_groups[name] = folium.FeatureGroup(name=name)
        folium.GeoJson(
            geometry,
            color=colors[color_id],
            name=name
        ).add_to(feature_groups[name])

    for fg in feature_groups.values():
        poly_map.add_child(fg)
    folium.LatLngPopup().add_to(poly_map)
    poly_map.fit_bounds(poly_map.get_bounds())
    poly_map.add_child(folium.map.LayerControl(collapsed=False))

    return poly_map


def plot_observations(
    observations: gpd.GeoDataFrame,
    show_heatmap: str | None = "all",
    padding: Tuple[int, int] | None = None,
) -> folium.folium.Map:
    """Visualize observations on a map

    Parameters
    ----------
    observations : gpd.GeoDataFrame
        GeoDataFrame with observations.
    show_heatmap : {"all", "hwc_animal"}
        If "all", include a heatmap of all observations.
        if "hwc_only", show a heatmap of human-wildlife-conflicts
        and animal observations only.
    padding : Tuple[int, int]
        Optional padding of the map, which is by default fit to the
        bounds of the observations.

    Returns
    -------
    poly_map : folium.folium.Map
        Map object.

    """
    poly_map = folium.Map(tiles="cartodbpositron")

    feature_groups = {
        "community_work": folium.FeatureGroup(name='Community'),
        "community": folium.FeatureGroup(name='Community'),
        "animal": folium.FeatureGroup(name='Animal sighting'),
        "hwc": folium.FeatureGroup(name='Human-wildlife-conflict'),
        "poi": folium.FeatureGroup(name='Point of interest'),
    }

    for _, obs in observations.iterrows():
        obs_type = obs["observationType"]
        if obs_type == "animal":
            icon_fmt = {
                "icon": "fa-paw",
                "color": "orange",
            }
        elif obs_type in ["community", "community_work"]:
            icon_fmt = {
                "icon": "fa-people-group",
                "color": "darkblue",
            }
        elif obs_type == "hwc":
            icon_fmt = {
                "icon": "fa-triangle-exclamation",
                "color": "red"
            }
        elif obs["observationType"] == "poi":
            icon_fmt = {
                "icon": "fa-leaf",
                "color": "darkgreen",
            }
        else:
            icon_fmt = {
                "icon": None,
                "color": "blue",
            }

        folium.Marker(
            [obs["geometry"].y, obs["geometry"].x],
            obs["conceptLabel"],
            icon=folium.Icon(**icon_fmt, prefix='fa')
        ).add_to(feature_groups[obs_type])

    if show_heatmap == "all":
        # add heatmap for observations of all types
        lat_lon = observations["geometry"].apply(lambda geom: [geom.y, geom.x])
        hm = HeatMap(lat_lon, name="Heatmap").add_to(folium.FeatureGroup())
        poly_map.add_child(hm)
    elif show_heatmap == "hwc_animal":
        # add heatmap for observations of type human-wildlife conflict ("hwc")
        lat_lon_hwc = observations.loc[
            observations["observationType"] == "hwc", "geometry"
        ].apply(lambda geom: [geom.y, geom.x])
        hm_hwc = HeatMap(
            lat_lon_hwc,
            name="HWC heatmap",
            gradient={
                0.4: 'brown',
                0.65: 'orange',
                1: 'red'},
        ).add_to(folium.FeatureGroup())
        poly_map.add_child(hm_hwc)

        # add heatmap for observations of "animal"
        lat_lon_animal = observations.loc[
            observations["observationType"] == "animal", "geometry"
        ].apply(lambda geom: [geom.y, geom.x])
        hm_animal = HeatMap(
            lat_lon_animal,
            name="Animal heatmap",
            gradient={
                0.4: 'blue',
                0.65: 'lime',
                1: 'green'}
        ).add_to(folium.FeatureGroup())
        poly_map.add_child(hm_animal)
    else:
        # Do not show any heatmap
        pass

    for fg in feature_groups.values():
        poly_map.add_child(fg)

    folium.LatLngPopup().add_to(poly_map)
    poly_map.fit_bounds(poly_map.get_bounds(), padding=padding)
    poly_map.add_child(folium.map.LayerControl(collapsed=False))

    return poly_map


def plot_tracks(track_geometry: gpd.GeoSeries) -> folium.folium.Map:
    """Visualize tracks on a map

    Parameters
    ----------
    track_geometry : gpd.GeoSeries
        GeoSeries with geometry of each track.

    Returns
    -------
    poly_map : folium.folium.Map
        Map object.

    """

    # Process track geometry so folium.PolyLine can handle it.
    tracks = track_geometry.explode(index_parts=True)
    tracks = tracks.apply(lambda point: (point.y, point.x)).to_frame()
    tracks = tracks.reset_index(level=0, names="track_id")

    poly_map = folium.Map(tiles="cartodbpositron")

    colors = plt.rcParams['axes.prop_cycle'].by_key()["color"]
    track_ids = tracks["track_id"].unique().tolist()
    for i, track_id in enumerate(track_ids):
        track = tracks.loc[tracks["track_id"] == track_id, "geometry"]
        color_id = i % (len(colors) - 1)  # cycle through default colors
        folium.PolyLine(
            track,
            color=colors[color_id],
            weight=5,
            opacity=0.8,
        ).add_to(poly_map)
    folium.LatLngPopup().add_to(poly_map)
    poly_map.fit_bounds(poly_map.get_bounds())

    return poly_map