import json
#import pprint
from urllib.request import urlopen

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

def get_IP_geo():

      # Initialize data structure based on format expected from call to web service
      # URL = http://ipinfo.io/json

      geo_URL = "http://ipinfo.io/json"

      geo_json = {
        "ip": "123.123.123.123",
        "city": "Dallas",
        "region": "Texas",
        "country": "US",
        "loc": ["32.7787", "-96.8217"],
        "postal": "75270",
        "org": "SoftLayer Technologies Inc."
        }

      # Open the URL and read the data, if successful decode bytestring and
      # split lat and long into separate strings

      try:
          webUrl = urlopen (geo_URL)
          if (webUrl.getcode() == 200):
              geo_data = webUrl.read()
              geo_json = json.loads(geo_data.decode('utf-8'))
              geo_json['loc'] = geo_json['loc'].split(',')
          else:
              print ("Geo service unavailable, using default location")
      except:
          print ("Error opening: {}, using default location".format(geo_URL))

      #pprint.pprint (geo_json)

      return geo_json
