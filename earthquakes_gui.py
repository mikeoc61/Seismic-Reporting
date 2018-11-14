#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+---------------------------------------------------------------------
+ Query, sort, format and output USGS earthquate data
+
+ Uses Tkinter to provide GUI
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

import sys
import json
from haversine import calc_dist as dist

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected version: {}".format \
          (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()
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

        if (webUrl.getcode() == 200):
            data = webUrl.read()
            sys.stdout.write = redirector
            print ("From: {}".format(quakeData))
            printResults(data)
        else:
            print ("Can't retrieve quake data " + str(webUrl.getcode()))

    def clear(self):

        result_box.delete(1.0, 'end')

# Define stdout redirector so print output goes to GUI textbox
# result_box widget is defined as global and set in USGS_Gui()

def redirector(inputStr):
    result_box.insert(INSERT, inputStr)

# Lat and long for my Zipcode per https://www.latlong.net
# Used to calculate relative distance from events to my location

my_lat  =  33.096470
my_long = -96.887009

def printResults (data):

  # Load the string data into a local dictionary

  quakes_json = json.loads(data.decode('utf-8'))

  if "title" in quakes_json["metadata"]:
      count = quakes_json["metadata"]["count"];
      print ("Recorded {} events from {}".format(count, quakes_json["metadata"]["title"]))

  # for each event, calculate distance from my coordinates and add value to a
  # new dictionary mapList { id : distance } we will use to sort raw event data.

  mapList = {}
  max_mag = 0

  for i in quakes_json["features"]:
      mag = i["properties"]["mag"]
      if mag >= max_mag:
          max_mag = mag
          max_place = i["properties"]["place"]
      long = i["geometry"]["coordinates"][0]
      lat  = i["geometry"]["coordinates"][1]
      distance = dist(lat, long, my_lat, my_long)
      mapList.update({i['id']:distance})

  biggest = "{:2.1f} at {}".format(max_mag, max_place)
  print ("Largest recorded event was magnitude {}".format(biggest))

  # Sort mapList { id : distance } dictionary by distance value kv[1]

  sorted_map = sorted(mapList.items(), key=lambda kv: kv[1])

  # Loop through distance sorted event ids (outer loop) and original quake data
  # (inner loop) comparing id values as we go. When we have a match, output the
  # relevant event data. Limit output to max_distance value

  max_dist = 5000

  # Print nicely formatted header

  print ("\n      Sorted events nearest to coordinates: {} : {} \n{}" \
        .format(my_lat, my_long, '-'*78))

  # print sorted events, one per line

  for i in sorted_map:
      for k in quakes_json["features"]:
          if k["id"] == i[0] and i[1] <= max_dist:
              print ("{:4.2f} centered {:40.38} distance: {:6.2f} miles".format(
                            k["properties"]["mag"],
                            k["properties"]["place"],
                            i[1]))

def main():

    root = Tk()
    USGS_Gui(root)
    root.mainloop()

if __name__ == "__main__": main()
