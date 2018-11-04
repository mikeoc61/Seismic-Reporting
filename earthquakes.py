#!/usr/bin/env python3

'''
+ Do some interesting stuff with USGS earthquate data
'''

import sys
import math
import json
from haversine import calc_dist as dist

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, not Python 2.x".format(sys.argv[0]))
    raise SystemExit()

try:
    from urllib.request import urlopen
except ImportError as e:
    print ("Unable to import urlib.request: {}".format(e))
    raise SystemExit()

# Lat and long for Zipcode 75056 per https://www.latlong.net
# Used to calculate relative distance from event to my location

my_lat = 33.096470
my_long = -96.887009

def get_dist(quake):
    return quake.get(['features']['distance'], math.inf)

def printResults(data):

  '''
  JSON Format data description @:
  https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
  '''
  # Use the json module to load the string data into a dictionary
  quakes_json = json.loads(data)

  kl = list(quakes_json.keys())
  # print (kl)

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"];
      print ("Recorded {} events in {}".format(count, quakes_json["metadata"]["title"]))

  # for each event, calculate distance from my coordinates and add to dictionary
  # and append id key and distance value pair to new dictionary for sorting

  events = {}

  for i in quakes_json["features"]:
    coords = i["geometry"]["coordinates"]
    long = coords[0]
    lat = coords[1]
    i['distance'] = dist(lat, long, my_lat, my_long)
    events.update({i['id']:i['distance']})

  # Sort { id : distance } key pair dictionary by distance

  sorted_events = sorted(events.items(), key=lambda kv: kv[1])

  # print ("sorted=", sorted_events)

  # Now loop through distance sorted events and original quake data comparing
  # ids as we go. When we have a match, output the event location and distance

  print("\n    Sorted events by distance from: {} : {}".format(my_lat, my_long), flush=True)
  print("-"*64)
  for i in sorted_events:
      #print ("i=", i[0])
      for k in quakes_json["features"]:
          #print ("k=", k)
          if k["id"] == i[0] and k["distance"] <= 5000:
              print ("{:4.2f} {:40.38} distance: {:6.2f} miles".format(
                            k["properties"]["mag"],
                            k["properties"]["place"],
                            k["distance"])
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
