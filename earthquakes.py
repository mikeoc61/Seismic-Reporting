#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+---------------------------------------------------------------------
+ Query, sort, format and output USGS earthquate data
+
+ See: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
+
+ for info on request options and data formats
+---------------------------------------------------------------------
'''

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

import sys
import pprint
from output import printResults

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected version: {}".format \
          (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()
else:
    from urllib.request import urlopen

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

if __name__ == "__main__": main()
