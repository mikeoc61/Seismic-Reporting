from __future__ import print_function
import json
import sys

#import pprint

if sys.version_info <= (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

def get_IP_geo():

      # Initialize data structure based on format expected from call to web service
      # URL = http://ipinfo.io/json
      # Also see: https://ipinfo.io/missingauth for licensing terms

      geo_URL = "http://ipinfo.io/json"

      geo_json = {
        "ip": "123.123.123.123",
        "city": "Kailua-Kona",
        "region": "Hawaii",
        "country": "US",
        "loc": "19.6402,-155.9991",
        "postal": "96740",
        "org": "SoftLayer Technologies Inc.",
        "timezone": "Pacific/Honolulu",
        "readme": "https://ipinfo.io/missingauth"
        }

      # Open the URL and read the data, if successful decode bytestring and
      # split lat and long into separate strings
      try:
          webUrl = urlopen (geo_URL)
      except:
          print("Error opening: {}, using default location".format(geo_URL))
      else:
          if (webUrl.getcode() == 200):
              geo_data = webUrl.read()
              geo_json = json.loads(geo_data.decode('utf-8'))
              geo_json['loc'] = geo_json['loc'].split(',')
          else:
              print("webUrl.getcode() returned: {}".format(webUrl.getcode()))
              print("Using default location data")

      return geo_json
