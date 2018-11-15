import json
from urllib import request
from haversine import calc_dist as dist

# Lat and long for my Zipcode per https://www.latlong.net
# Used to calculate relative distance from events to my location

#my_lat  =  33.096470
#my_long = -96.887009

def printResults(data):

  # Initialize data structure based on format expected from call to web service
  # URL = http://ipinfo.io/json

  geo_data = {
    "ip": "123.123.123.123",
    "hostname": "myhost.net",
    "city": "Dallas",
    "region": "Texas",
    "country": "US",
    "loc": "32.7787,-96.8217",
    "postal": "75270",
    "org": "SoftLayer Technologies Inc."
    }

  try:
      geo_data = json.load(request.urlopen('http://ipinfo.io/json'))
  except Exception as e:
      print('Error determining geolocation data: {}'.format(e))
      print("Using default settings")

  my_lat, my_long = geo_data['loc'].split(',')

  # Load the earthquake string data into a local dictionary

  quakes_json = json.loads(data.decode('utf-8'))

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"];
      print ("Recorded {} events from {}".format(count, quakes_json["metadata"]["title"]))

  # for each event, calculate distance from my coordinates and add value
  # to a new dictionary { id : distance } used to sort raw event data.

  mapList = {}
  max_mag = 0

  for i in quakes_json["features"]:
      #if max_mag == 0: pprint.pprint(i)
      mag = i["properties"]["mag"]
      if mag >= max_mag:
          max_mag = mag
          max_place = i["properties"]["place"]
      long = i["geometry"]["coordinates"][0]
      lat  = i["geometry"]["coordinates"][1]
      distance = dist(lat, long, float(my_lat), float(my_long))
      mapList.update({i['id']:distance})

  biggest = "{:2.1f} at {}".format(max_mag, max_place)
  print ("Strongest event was magnitude {}".format(biggest))

  # Sort { id : distance } key pair dictionary by distance value kv[1]

  sorted_map = sorted(mapList.items(), key=lambda kv: kv[1])

  # Loop through distance sorted event ids (outer loop) and original quake data
  # (inner loop) comparing id values as we go. When we have a match, output the
  # event location and distance. Limit output to max_events value

  max_miles = 6000

  # Print nicely formatted header

  print ("\nSorted events nearest to: {loc} [{city}, {region}, {country}]" \
        .format(**geo_data))

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
