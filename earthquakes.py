#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from output import printResults

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


if sys.version_info <= (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

def main():

  # Using data feed from the USGS
  # quakeData = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
  # quakeData = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"
  quakeData = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"

  # Open the URL and read the data, call printResults() to format and output

  try:
      webUrl = urlopen(quakeData)
  except:
      print ("Error opening: {}".format(quakeData))
  else:
      if (webUrl.getcode() == 200):
          data = webUrl.read()
          printResults(data)
      else:
          print ("Error from USGS server, cannot retrieve data " + str(webUrl.getcode()))

if __name__ == "__main__": main()
