"""Wrapper SensingClues-class for usage in Ecoscope"""

import io
import math
import warnings
from typing import List, Union

import geopandas as gpd
import numpy as np
import pandas as pd
import requests

from sensingcluespy import sclogging
from sensingcluespy.sensingclues_api import SensingClues

logger = sclogging.get_sc_logger()

class SensingCluesEcoscope(object):
    """Class to extract SensingClues-data through Ecoscope"""

    def __init__(self, username: str, password: str):
        """Automatically log in when initiating class and obtain available groups

        :param username: Username for SensingClues Focus
        :param password: Password for SensingClues Focus
        """
        self.sc = SensingClues(username=username, password=password)
        self.groups = self.sc.get_groups()

    def get_events(
        self,
        groups: Union[str, List],
        event_ids: str = None,
        event_type: list = None,
        since: str = None,
        until: str = None,
        include_subconcepts: bool = True,
        **kwargs,
    ) -> gpd.GeoDataFrame:
        """Method to acquire events data from SensingClues

        Extra (filter) arguments can be passed to this method via kwargs.
        For an overview of the extra arguments allowed, see
        the description of make_query() in helper_functions.py.

        :param groups: Name(s) of groups to query from, passed as a string
            or as a list of strings, e.g. "focus-project-1234".
        :param include_subconcepts: If filtering on concepts (using the
            concepts-kwarg), this argument allows you to include or exclude
            observations related to concepts lower in the hierarchy than the
            concept you filtered on.
            For instance, if you filter on 'animal' (concepts =
            "https://sensingclues.poolparty.biz/SCCSSOntology/186"),
            you will also obtain entries for e.g. 'hippo' (which is an
            'animal') if include_subconcepts is True. Default is True.

        :returns: Dataframe with available observations, in line with the
            query parameters specified in kwargs (if any).
        """

        query_text = None
        # Filter on eventId if it is given
        if event_ids is not None:
            query_text = f"entityId: '{event_ids}'"

        events = self.sc.get_observations(
            groups=groups,
            include_subconcepts=include_subconcepts,
            query_text=query_text,
            **kwargs,
        )

        return events

    def get_event_types():
        pass
