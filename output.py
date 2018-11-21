from __future__ import print_function
import json

from IP_geo import get_IP_geo
from haversine import calc_dist as dist

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

def printResults(data):

  # Load the earthquake string data into a local dictionary

  quakes_json = json.loads(data.decode('utf-8'))

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"]
      print ("Recorded {} events from {}".format(count, quakes_json["metadata"]["title"]))

  # Call get_IP_geo() to dynamically determine location based on IP addr lookup
  # Convert strings to float here to save processing time in event sort loop

  my_geo = get_IP_geo()

  my_lat  = float (my_geo['loc'][0])
  my_long = float (my_geo['loc'][1])

  # For each event, calculate distance from my coordinates and add event id
  # and distance from me as a tuple to mapList[] which will then be used to
  # sort raw event data by distance

  mapList = []
  max_mag = 0

  for i in quakes_json["features"]:
      #if max_mag == 0: pprint.pprint(i)
      mag = i["properties"]["mag"]
      if mag >= max_mag:
          max_mag, max_place = mag, i["properties"]["place"]
      long = i["geometry"]["coordinates"][0]
      lat  = i["geometry"]["coordinates"][1]
      distance = dist(lat, long, my_lat, my_long)
      mapList.append((i['id'],distance))

  biggest = "{:2.1f} at {}".format(max_mag, max_place)
  print ("Strongest event was magnitude {}".format(biggest))

  # Sort mapList list of (id, distance) tuples by distance

  sorted_map = sorted(mapList, key=lambda tup: tup[1])

  # Loop through distance sorted event ids (outer loop) and original quake data
  # (inner loop) comparing id values as we go. When we have a match, output the
  # event location and distance. Limit output to max_events value

  max_miles = 6000

  # Print nicely formatted header

  print ("\nSorted events nearest to: {loc[0]}N {loc[1]}E [{city}, {region}, {country}]" \
        .format(**my_geo))

  print ("\n{}".format('-'*78))

  # output sorted seismic events, one per line

  for i in sorted_map:
      for k in quakes_json["features"]:
          if k["id"] == i[0] and i[1] <= max_miles:
              print ("{:4.2f} centered {:40.38} distance: {:6.2f} miles".format(
                            k["properties"]["mag"],
                            k["properties"]["place"],
                            i[1])
                            )
