#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core logic for the Seismic-Reporting tool.

Builds USGS FDSN event-service queries, decodes the GeoJSON response into
Quake records, and renders sorted reports. Statistics, sorting and
formatting are pure functions with no GUI dependency, so the same pipeline
backs both the Tkinter GUI and the command-line front end.

FDSN event service: https://earthquake.usgs.gov/fdsnws/event/1/
"""

import datetime
import json
from dataclasses import dataclass
from operator import attrgetter
from statistics import mean, median
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from haversine import calc_dist

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2025"

# USGS FDSN event query endpoint (GeoJSON output).
FDSN_ENDPOINT = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Sort codes. Values intentionally match the Tkinter IntVar used by the GUI.
SORT_MAGNITUDE = 0
SORT_LOCATION  = 1
SORT_DISTANCE  = 2
SORT_TIME      = 3

_SORT_LABEL = {
    SORT_MAGNITUDE: "MAGNITUDE",
    SORT_LOCATION:  "LOCATION",
    SORT_DISTANCE:  "DISTANCE",
    SORT_TIME:      "DATE & TIME",
}

# Returned by fetch_geojson() when FDSN reports HTTP 204 (zero matches).
_EMPTY_GEOJSON = (b'{"type":"FeatureCollection",'
                  b'"metadata":{"count":0,"title":"USGS FDSN query (no events)"},'
                  b'"features":[]}')


@dataclass
class Quake:
    """A single seismic event, with distance pre-computed from the observer."""
    mag: float
    place: str                      # raw USGS place string
    distance_km: float
    time: datetime.datetime


@dataclass
class Origin:
    """Observer location: the reference point for distance calculations."""
    lat: float
    lon: float
    name: str


# Default observer: a fixed home location replaces the old IP-geolocation
# lookup (a self-hosted tool does not move).
DEFAULT_ORIGIN = Origin(19.6402, -155.9991, "Kailua-Kona, Hawaii")


# --------------------------------------------------------------------------
# Helpers (behaviour carried verbatim from the original implementation)
# --------------------------------------------------------------------------

def unique_mode(values):
    """Return the most frequent value; ties resolved toward the larger count.

    NOTE: when every value is distinct (the common case for float
    magnitudes) this returns the *first* element of `values`, so callers
    must pass the list in a stable, meaningful order. See magnitude_summary.
    """
    counted = [[values.count(n), n] for n in values]
    counted.sort(key=lambda x: x[0], reverse=True)
    return counted[0][1]


def check_type(val):
    """Coerce an int/float to float; anything else (e.g. JSON null) -> 0.00."""
    if isinstance(val, (float, int)):
        return float(val)
    return 0.00


def format_place(place):
    """Re-order a USGS place string so the broad region leads."""
    _regions = ["Region", "Ocean", "Ridge", "Sea", "Passage", "Rise", "Gulf"]

    _new_list = place.capitalize().split()
    for word in _new_list:
        if word in _regions:
            return ' '.join(_new_list)

    _new_list = place.split(', ')
    _new_list.reverse()
    _new_list[0] = _new_list[0].title()
    return ', '.join(_new_list)


def _place_key(quake):
    """Sort key for location ordering (region-first form)."""
    return format_place(quake.place)


# --------------------------------------------------------------------------
# Pipeline: build URL -> fetch -> parse -> (summary) -> sort -> format
# --------------------------------------------------------------------------

def build_fdsn_url(min_mag, starttime, endtime=None,
                   lat=None, lon=None, radius_km=None,
                   orderby='time', limit=None):
    """Construct a USGS FDSN event-query URL (GeoJSON format).

    `starttime`/`endtime` are ISO-8601 strings (UTC assumed). When `lat`,
    `lon` and `radius_km` are all supplied the query is restricted to that
    radial region; otherwise it is global. Server-side filtering replaces
    the old client-side distance filtering.
    """
    params = {
        'format': 'geojson',
        'starttime': starttime,
        'minmagnitude': min_mag,
        'orderby': orderby,
    }
    if endtime is not None:
        params['endtime'] = endtime
    if lat is not None and lon is not None and radius_km is not None:
        params['latitude'] = lat
        params['longitude'] = lon
        params['maxradiuskm'] = radius_km
    if limit is not None:
        params['limit'] = limit
    return FDSN_ENDPOINT + '?' + urlencode(params)


def fetch_geojson(url, timeout=10):
    """Fetch raw GeoJSON bytes from a USGS URL.

    Returns an empty FeatureCollection on HTTP 204 (FDSN: query valid but
    zero events matched). Raises URLError/HTTPError on transport failure,
    RuntimeError on any other non-200 response.
    """
    response = urlopen(url, timeout=timeout)
    code = response.getcode()
    if code == 204:
        return _EMPTY_GEOJSON
    if code != 200:
        raise RuntimeError('USGS server returned HTTP {}'.format(code))
    return response.read()


def parse_quakes(data, origin):
    """Decode GeoJSON bytes into (list[Quake], metadata dict).

    Quakes are returned in feed order. `origin` is an Origin instance;
    its coordinates are the reference for the distance calculation.
    """
    geo = json.loads(data.decode('utf-8'))

    quakes = []
    for feature in geo['features']:
        lon, lat = feature['geometry']['coordinates'][0:2]
        props = feature['properties']
        quakes.append(Quake(
            mag=check_type(props['mag']),
            place=props['place'],
            distance_km=calc_dist(lat, lon, origin.lat, origin.lon),
            time=datetime.datetime.fromtimestamp(props['time'] / 1000.0),
        ))

    metadata = geo.get('metadata', {})
    meta = {
        'count': metadata.get('count', len(quakes)),
        'title': metadata.get('title', 'USGS FDSN Earthquakes'),
    }
    return quakes, meta


def magnitude_summary(quakes):
    """One-line magnitude statistics, or a 'no results' notice.

    Must be called on the feed-order list (before sorting): unique_mode
    is order-sensitive when magnitudes are distinct.
    """
    mags = [q.mag for q in quakes]
    if not mags:
        return ('** No results found. '
                'Try reducing Magnitude or increasing Time Period **')
    return ('Magnitude Max = {:2.2f}, Mean = {:2.2f}, '
            'Median = {:2.2f}, Mode = {:2.2f}').format(
        max(mags), mean(mags), median(mags), unique_mode(mags))


def sort_quakes(quakes, sort_code, reverse=False):
    """Return a new list of quakes ordered by the requested sort code."""
    if sort_code == SORT_LOCATION:
        key = _place_key
    elif sort_code == SORT_DISTANCE:
        key = attrgetter('distance_km')
    elif sort_code == SORT_TIME:
        key = attrgetter('time')
    else:
        key = attrgetter('mag')
    return sorted(quakes, key=key, reverse=reverse)


def format_report(quakes, meta, origin, sort_code, stats_line, elapsed_s, width):
    """Render a complete fixed-width text report as a single string.

    `quakes` should already be sorted; `stats_line` is the precomputed
    magnitude_summary() result. Returns the string the GUI inserts into
    its text box (or the CLI prints to stdout).
    """
    out = []

    out.append('{:*^{}}\n\n'.format(' [Event statistical Analysis] ', width))
    out.append('{:^{}}\n\n'.format(
        'Recorded {} events from {}'.format(meta['count'], meta['title']),
        width))
    out.append('{:^{}}\n\n'.format(stats_line, width))
    out.append('{:^{}}\n'.format(
        'Total processing time: {:2.2f} seconds'.format(elapsed_s), width))

    if sort_code == SORT_DISTANCE:
        banner = ' [Events are sorted by DISTANCE from: {}] '.format(origin.name)
    elif sort_code in _SORT_LABEL:
        banner = ' [Events are sorted by {}] '.format(_SORT_LABEL[sort_code])
    else:
        banner = ' [Have no idea how we are sorting] '
    out.append('\n{:*^{}}\n\n'.format(banner, width))

    for q in quakes:
        if q.mag >= 0.0:
            place = format_place(q.place) if sort_code == SORT_LOCATION else q.place
            stamp = q.time.strftime("%H:%M:%S on %m/%d")
            out.append(
                '{:4.2f} centered {:46.45} distance: {:>8.2f} km at {}\n'.format(
                    q.mag, place, q.distance_km, stamp))

    return ''.join(out)
