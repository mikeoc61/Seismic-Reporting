# Seismic-Reporting

Python3 program which queries USGS earthquake historical data and outputs results
sorted by distance from a given coordinate. For more info on the data feed, please
see: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

IP_geo.py contains code to dynamically fetch current location data based on IP lookup

earthquakes.py is the command line version and imports haversine.py and IP_geo.py

earthquakes_gui.py is the GUI version built with Tkinter and relies on output.py.
The GUI version is much more powerful as it allows dynamic control of both the
sample time interval as well as the sort criteria (Magnitude, Place, Distance)

output.py is imported by earthquakes_gui.py and does the actual output formatting.
This modules also imports haversine.py and imports IP_geo.py to determine local
coordinates based upon IP address lookup from "http://ipinfo.io/json"

The Haversine formula is used to calculate distance relative to starting coordinates
