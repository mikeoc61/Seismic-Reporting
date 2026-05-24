# Seismic-Reporting

Queries the USGS earthquake catalog and lists events sorted by magnitude,
location, distance, or time. Distance is measured (Haversine) from a chosen
observer coordinate.

## Data source

Events come from the USGS FDSN event service, which supports server-side
filtering by magnitude, time window, and radial region:

<https://earthquake.usgs.gov/fdsnws/event/1/>

## Install

The package uses a standard `src/` layout and a PEP 517 build. Install it
(editable, for development) into a virtual environment:

```
git clone https://github.com/mikeoc61/Seismic-Reporting
cd Seismic-Reporting
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This puts two commands on `PATH`: `seismic` (CLI) and `seismic-gui` (GUI).
Only the standard library is required at runtime; `[dev]` adds pytest, ruff,
and mypy.

## Project layout

```
src/seismic_reporting/
  core.py        FDSN URL construction, GeoJSON parsing into Quake records,
                 magnitude statistics, sorting, report formatting. No GUI
                 or argparse dependency; shared by both front ends.
  cli.py         Command-line front end (entry point: seismic).
  gui.py         Tkinter GUI front end (entry point: seismic-gui).
  haversine.py   Great-circle distance between two coordinates.
tests/           pytest suite, with GeoJSON fixtures under tests/fixtures/.
```

## Command-line usage

```
seismic                                  # M2.5+, past day, near home
seismic --radius 300 --min-mag 1.0       # within 300 km of home
seismic --lat 37.77 --lon -122.42 --radius 100 --sort time --reverse
seismic --file saved.geojson --sort magnitude
```

Run `seismic --help` for the full option list. `--file` reads a saved
GeoJSON document instead of querying USGS (useful offline or for testing).

## GUI usage

```
seismic-gui
```

Select a time period, minimum magnitude, sort field, and sort order, then
press **Get Results**. The GUI queries globally and sorts by distance from
the fixed home location (`DEFAULT_ORIGIN` in `core.py`); use
`seismic --radius` for radial filtering or a different observer coordinate.

## Development

```
pytest          # run the test suite
ruff check .    # lint
mypy src        # type-check (strict)
```
