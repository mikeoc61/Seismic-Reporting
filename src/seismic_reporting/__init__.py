"""Seismic-Reporting: query the USGS FDSN event service and report quakes.

The package exposes a network/GUI-free core pipeline (build URL -> fetch ->
parse -> summarise -> sort -> format) plus two front ends: a command-line
tool (:mod:`seismic_reporting.cli`) and a Tkinter GUI
(:mod:`seismic_reporting.gui`).
"""

from __future__ import annotations

from seismic_reporting.core import (
    DEFAULT_ORIGIN,
    FDSN_ENDPOINT,
    SORT_DISTANCE,
    SORT_LOCATION,
    SORT_MAGNITUDE,
    SORT_TIME,
    Origin,
    Quake,
    build_fdsn_url,
    fetch_geojson,
    format_report,
    magnitude_summary,
    parse_quakes,
    sort_quakes,
)
from seismic_reporting.haversine import EARTH_RADIUS_KM, calc_dist

__version__ = "1.1.0"
__author__ = "Michael E. O'Connor"

__all__ = [
    "DEFAULT_ORIGIN",
    "FDSN_ENDPOINT",
    "SORT_DISTANCE",
    "SORT_LOCATION",
    "SORT_MAGNITUDE",
    "SORT_TIME",
    "EARTH_RADIUS_KM",
    "Origin",
    "Quake",
    "build_fdsn_url",
    "calc_dist",
    "fetch_geojson",
    "format_report",
    "magnitude_summary",
    "parse_quakes",
    "sort_quakes",
    "__version__",
]
