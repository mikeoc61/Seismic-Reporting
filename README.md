# Seismic-Reporting

Queries the USGS earthquake catalog and lists events sorted by magnitude,
location, distance, or time. Distance is measured (Haversine) from a chosen
observer coordinate.

## Data source

Events come from the USGS FDSN event service, which supports server-side
filtering by magnitude, time window, and radial region:

<https://earthquake.usgs.gov/fdsnws/event/1/>

## Files

- `output.py` — core logic: FDSN URL construction, GeoJSON parsing into
  `Quake` records, magnitude statistics, sorting, and report formatting.
  No GUI dependency; shared by both front ends.
- `cli.py` — command-line front end. Exposes observer coordinates, radial
  filtering, magnitude, time window, and sort options as arguments.
- `earthquakes_gui.py` — Tkinter GUI front end. Distances are measured from
  a fixed home location (`DEFAULT_ORIGIN` in `output.py`).
- `haversine.py` — great-circle distance between two coordinates.

## Command-line usage

```
cli.py                                  # M2.5+, past day, near home
cli.py --radius 300 --min-mag 1.0       # within 300 km of home
cli.py --lat 37.77 --lon -122.42 --radius 100 --sort time --reverse
cli.py --file saved.geojson --sort magnitude
```

Run `cli.py --help` for the full option list. `--file` reads a saved
GeoJSON document instead of querying USGS (useful offline or for testing).

## GUI usage

```
python3 earthquakes_gui.py
```

Select a time period, minimum magnitude, sort field, and sort order, then
press **Get Results**. The GUI queries globally and sorts by distance from
the fixed home location; use `cli.py --radius` for radial filtering or a
different observer coordinate.
