#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+---------------------------------------------------------------------
+ Query, sort, format and output USGS earthquate data
+
+ This file used to experiment with alternative techniques
+ This file should be copied to earthquakes.py when satisfied and
+ not pushed to github!
+
+ See: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
+
+ for info on request options and data formats
+---------------------------------------------------------------------
'''

_author__     = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

from tkinter import *
from tkinter import ttk
from timeit import default_timer as timer

import sys
import json
from statistics import mean, mode, median
#import pprint
from haversine import calc_dist as dist

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

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected version: {}".format \
          (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    #raise SystemExit()
    from urllib2.request import urlopen
else:
    from urllib.request import urlopen

# Construct GUI

class USGS_Gui:

    def __init__(self, master):
        global result_box

        master.title('USGS Earthquake Data')
        frame0 = ttk.Panedwindow(master, orient = HORIZONTAL)
        frame0.pack(fill = BOTH, expand = True)
        frame1 = ttk.Frame(frame0, width = 100, height = 300, relief = SUNKEN)
        frame2 = ttk.Frame(frame0, width = 500, height = 300, relief = SUNKEN)
        frame0.add(frame1, weight = 1)
        frame0.add(frame2, weight = 4)
        Label(frame1, text = "Select sample period", justify = LEFT).pack()
        self.period = StringVar()
        day = ttk.Radiobutton(frame1, text = "Day", variable = self.period, value = "day")
        week = ttk.Radiobutton(frame1, text = "Week", variable = self.period, value = "week")
        month = ttk.Radiobutton(frame1, text = "Month", variable = self.period, value = "month")
        self.period.set("day")
        day.pack(anchor = 'w')
        week.pack(anchor = 'w')
        month.pack(anchor = 'w')
        result_button = ttk.Button(frame1)
        result_button.config(text = "Get Results", command = self.submit)
        result_button.pack(anchor = 's')
        result_box = Text(frame2)
        result_box.grid(row = 0, column = 0)
        scrollbar = ttk.Scrollbar(frame2, orient = VERTICAL, command = result_box.yview)
        scrollbar.grid(row = 0, column = 1, sticky = 'ns')
        result_box.config(yscrollcommand = scrollbar.set)

    def submit(self):

        self.clear()

        quake_URL_base = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"

        quakeData = quake_URL_base + "2.5_" + self.period.get() + ".geojson"

        # Open the URL and read the data
        try:
            webUrl = urlopen (quakeData)
        except:
            print ("Fatal error opening: {}".format(quakeData))
            raise SystemExit()
        else:
            if (webUrl.getcode() == 200):
                data = webUrl.read()
                sys.stdout.write = redirector
                printResults(data)
                sys.stdout.write = sys.__stdout__
            else:
                print ("Can't retrieve quake data " + str(webUrl.getcode()))

    def clear(self):

        result_box.delete(1.0, 'end')

# Define stdout redirector so print output goes to GUI textbox
# result_box widget is defined as global and set in USGS_Gui()

def redirector(inputStr):
    result_box.insert(INSERT, inputStr)

# Return largest, most commonly occuring numerical value when no single mode
# value exists. Statistics.mode() throws an exception when there is no single
# unique mode value

def unique_mode(a_list):
    numeral=[[a_list.count(n), n] for n in a_list]
    numeral.sort(key=lambda x:x[0], reverse=True)
    #print(numeral)
    return(numeral[0][1])

def printResults (data):

  mapList = {}
  max_mag = 0
  magData = []

  # Call get_IP_geo() to dynamically determine location based on IP addr lookup
  # Convert strings to float here to save processing time in event sort loop

  my_geo = get_IP_geo()

  my_lat  = float (my_geo['loc'][0])
  my_long = float (my_geo['loc'][1])

  # Load the string data into a local dictionary

  quakes_json = json.loads(data.decode('utf-8'))

  start = timer()

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"];
      print ("Recorded total of {} events from {}".format(count, quakes_json["metadata"]["title"]))

  # for each event, calculate distance from my coordinates and add value to a
  # new dictionary mapList { id : distance } we will use to sort raw event data.

  for i in quakes_json["features"]:
      # if max_mag == 0: pprint.pprint(i)
      mag = i["properties"]["mag"]
      if mag >= max_mag:
          max_mag = mag
          max_place = i["properties"]["place"]
      long = i["geometry"]["coordinates"][0]
      lat  = i["geometry"]["coordinates"][1]
      distance = dist(lat, long, my_lat, my_long)
      mapList.update({i['id']:distance})
      magData.append(mag)
      #mapList.append((i['id'], distance))

  #pprint.pprint (mapList)
  biggest = "{:2.2f} - {:.40s}".format(max_mag, max_place)
  print ("Largest event was magnitude {}".format(biggest))

  print("Magnitude Mean = {:2.2f}, Median = {:2.2f}, Mode = {:2.2f}" \
      .format(mean(magData), median(magData), unique_mode(magData)))

  # Sort mapList { id : distance } dictionary by distance value kv[1]

  #sorted_map = sorted(mapList, key=lambda tup: tup[1])
  sorted_map = sorted(mapList.items(), key=lambda kv: kv[1])


  # Loop through distance sorted event ids (outer loop) and original quake data
  # (inner loop) comparing id values as we go. When we have a match, output the
  # relevant event data. Limit output to max_distance value

  max_dist = 20000

  # Print nicely formatted header

  header = ' [Sorted events nearest to: {} : {}] '.format(my_lat, my_long)
  print('\n{:*^78}\n'.format(header))

  # print sorted events, one per line

  for i in sorted_map:
      for k in quakes_json["features"]:
          if k["id"] == i[0] and i[1] <= max_dist:
              print("{:4.2f} centered {:40.38} distance: {:6.2f} miles".format(
                            k["properties"]["mag"],
                            k["properties"]["place"],
                            i[1]))

  print ("Processed data in {:2.3f} seconds".format(timer() - start))

def main():

    root = Tk()

    USGS_Gui(root)

    root.mainloop()

if __name__ == "__main__": main()
