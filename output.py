import json
from haversine import calc_dist as dist

# Lat and long for my Zipcode per https://www.latlong.net
# Used to calculate relative distance from events to my location

my_lat  =  33.096470
my_long = -96.887009

def printResults(data):

  # Load the string data into a local dictionary

  #quakes_json = json.loads(data)
  quakes_json = json.loads(data.decode('utf-8'))

  # pprint.pprint(quakes_json)

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"];
      print ("Recorded {} events from {}".format(count, quakes_json["metadata"]["title"]))

  # for each event, calculate distance from my coordinates and add value
  # to a new dictionary { id : distance } we will use to sort raw event data.

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
      distance = dist(lat, long, my_lat, my_long)
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

  print ("\n      Sorted events nearest to coordinates: {} : {} \n{}" \
        .format(my_lat, my_long, '-'*78))

  # print events, one per line

  for i in sorted_map:
      for k in quakes_json["features"]:
          if k["id"] == i[0] and i[1] <= max_miles:
              print ("{:4.2f} centered {:40.38} distance: {:6.2f} miles".format(
                            k["properties"]["mag"],
                            k["properties"]["place"],
                            i[1])
                            )
