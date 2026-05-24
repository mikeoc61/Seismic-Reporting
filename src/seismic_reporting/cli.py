"""Command-line front end for the Seismic-Reporting tool.

Queries the USGS FDSN event service and prints earthquake events sorted
by magnitude, location, distance or time. Query parameters that the GUI
hard-codes are exposed here as command-line options.

Examples:
    seismic                                  # M2.5+, past day, near home
    seismic --radius 300 --min-mag 1.0       # within 300 km of home
    seismic --lat 37.77 --lon -122.42 --radius 100 --sort time --reverse
    seismic --file saved.geojson --sort magnitude
"""

from __future__ import annotations

import argparse
import datetime
import sys
from timeit import default_timer as timer
from urllib.error import HTTPError, URLError

from seismic_reporting.core import (
    DEFAULT_ORIGIN,
    SORT_DISTANCE,
    SORT_LOCATION,
    SORT_MAGNITUDE,
    SORT_TIME,
    Origin,
    build_fdsn_url,
    fetch_geojson,
    format_report,
    magnitude_summary,
    parse_quakes,
    sort_quakes,
)

__author__ = "Michael E. O'Connor"
__copyright__ = "Copyright 2026"

_SORT_CODES: dict[str, int] = {
    'magnitude': SORT_MAGNITUDE,
    'location': SORT_LOCATION,
    'distance': SORT_DISTANCE,
    'time': SORT_TIME,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Define and parse command-line options."""
    parser = argparse.ArgumentParser(
        prog='seismic',
        description="Query USGS earthquake data and list events sorted by "
                    "magnitude, location, distance or time.")

    parser.add_argument('--lat', type=float, default=DEFAULT_ORIGIN.lat,
                        help='observer latitude (default: %(default)s)')
    parser.add_argument('--lon', type=float, default=DEFAULT_ORIGIN.lon,
                        help='observer longitude (default: %(default)s)')
    parser.add_argument('--name', default=DEFAULT_ORIGIN.name,
                        help='observer location label (default: %(default)s)')
    parser.add_argument('--radius', type=float, default=None, metavar='KM',
                        help='restrict to events within KM of the observer '
                             '(default: no radial limit)')
    parser.add_argument('--min-mag', type=float, default=2.5,
                        help='minimum magnitude (default: %(default)s)')
    parser.add_argument('--days', type=float, default=1.0,
                        help='look back this many days (default: %(default)s)')
    parser.add_argument('--sort', choices=sorted(_SORT_CODES),
                        default='distance',
                        help='sort field (default: %(default)s)')
    parser.add_argument('--reverse', action='store_true',
                        help='reverse the sort order')
    parser.add_argument('--limit', type=int, default=None,
                        help='maximum number of events to request')
    parser.add_argument('--width', type=int, default=100,
                        help='report width in characters (default: %(default)s)')
    parser.add_argument('--file', metavar='PATH', default=None,
                        help='read GeoJSON from PATH instead of querying USGS')
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run a query (or load a file) and print the formatted report."""
    args = parse_args(argv)
    origin = Origin(args.lat, args.lon, args.name)
    sort_code = _SORT_CODES[args.sort]

    if args.file:
        try:
            with open(args.file, 'rb') as handle:
                data = handle.read()
        except OSError as err:
            print('Error reading {}: {}'.format(args.file, err),
                  file=sys.stderr)
            return 1
    else:
        starttime = (datetime.datetime.now(datetime.timezone.utc)
                     - datetime.timedelta(days=args.days)
                     ).strftime('%Y-%m-%dT%H:%M:%S')
        url = build_fdsn_url(args.min_mag, starttime,
                             lat=args.lat, lon=args.lon,
                             radius_km=args.radius, limit=args.limit)
        try:
            data = fetch_geojson(url)
        except (URLError, HTTPError, RuntimeError) as err:
            print('Error retrieving data: {}'.format(err), file=sys.stderr)
            return 1

    start = timer()
    quakes, meta = parse_quakes(data, origin)
    stats = magnitude_summary(quakes)               # before sort: feed order
    quakes = sort_quakes(quakes, sort_code, args.reverse)
    report = format_report(quakes, meta, origin, sort_code, stats,
                           timer() - start, args.width)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
