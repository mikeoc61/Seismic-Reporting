# Seismic-Reporting

Python3 program which queries USGS earthquake historical data and outputs results
sorted by distance from a given coordinate.

IP_geo.py contains code to dynamically fetch current location data based on IP lookup

earthquakes.py is the command line version

earthquakes_gui.py is the GUI version built with Tkinter

Both command line and GUI versions import the output.py which does the actual output
formatting, imports haversine.py and imports IP_geo.py to determine local coordinates

The Haversine formula is used to calculate distance relative to starting coordinates
