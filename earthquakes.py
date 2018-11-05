#!/usr/bin/env python3

'''
+---------------------------------------------------------------------
+ Do some interesting stuff with USGS earthquate data
+
+ See: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
+
+ for info on request options and data formats
+---------------------------------------------------------------------
'''

_author__      = "Michael E. O'Connor"
__copyright__   = "Copyright 2018"

import sys
import math
import json
from urllib.request import urlopen
from haversine import calc_dist as dist

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, not Python 2.x".format(sys.argv[0]))
    raise SystemExit()

# Lat and long for my Zipcode per https://www.latlong.net
# Used to calculate relative distance from events to my location

my_lat  =  33.096470
my_long = -96.887009

def printResults(data):

  # Load the string data into a local dictionary

  quakes_json = json.loads(data)

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"];
      print ("Recorded {} events from {}".format(count, quakes_json["metadata"]["title"]))

  # for each event, calculate distance from my coordinates and add value
  # to a new dictionary { id : distance } we will use to sort raw event data.

  events = {}

  for i in quakes_json["features"]:
    coords = i["geometry"]["coordinates"]
    long = coords[0]
    lat = coords[1]
    distance = dist(lat, long, my_lat, my_long)
    events.update({i['id']:distance})

  # Sort { id : distance } key pair dictionary by distance value kv[1]

  sorted_events = sorted(events.items(), key=lambda kv: kv[1])

  # Loop through distance sorted event ids (outer loop) and original quake data
  # (inner loop) comparing id values as we go. When we have a match, output the
  # event location and distance. Limit output to max_events value

  max_events = 5000

  print("\n      Sorted events nearest to coordinates: {} : {}".format(
        my_lat, my_long))
  print("-"*78, flush=True)

  for i in sorted_events:
      for k in quakes_json["features"]:
          if k["id"] == i[0] and i[1] <= max_events:
              print ("{:4.2f} centered {:40.38} distance: {:6.2f} miles".format(
                            k["properties"]["mag"],
                            k["properties"]["place"],
                            i[1])
                            )

def main():

  # Using data feed from the USGS
  # quakeData = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
  # quakeData = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"
  quakeData = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"

  # Open the URL and read the data
  try:
      webUrl = urlopen(quakeData)
  except:
	  print ("Error opening: {}".format(quakeData))

  if (webUrl.getcode() == 200):
    data = webUrl.read()
    printResults(data)
  else:
    print ("Error from USGS server, cannot retrieve data " + str(webUrl.getcode()))

if __name__ == "__main__":
  main()
