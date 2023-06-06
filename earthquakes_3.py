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

_author__     = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

from tkinter import *
from tkinter import ttk
from timeit import default_timer as timer

import sys
import json
from statistics import mean, mode, median
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

        self.master = master
        self.master.title('USGS Earthquake Data')
        frame0 = ttk.Panedwindow(master, orient = HORIZONTAL)
        frame0.pack(fill = BOTH, expand = True)
        frame1 = ttk.Frame(frame0, width = 100, height = 300, relief = SUNKEN)
        frame2 = ttk.Frame(frame0, width = 500, height = 300, relief = SUNKEN)
        frame0.add(frame1, weight = 1)
        frame0.add(frame2, weight = 4)

        Label(frame1, text = "Sample period", bg="black", fg="white", justify = LEFT).pack(fill=X)
        self.period = StringVar()
        _day = ttk.Radiobutton(frame1, text = "Past Day", variable = self.period, value = "day")
        _week = ttk.Radiobutton(frame1, text = "Past Week", variable = self.period, value = "week")
        _month = ttk.Radiobutton(frame1, text = "Past Month", variable = self.period, value = "month")
        _day.pack(anchor = 'w')
        _week.pack(anchor = 'w')
        _month.pack(anchor = 'w')
        self.period.set("day")

        Label(frame1, text = "Sort By", bg="black", fg="white", justify = LEFT).pack(fill=X)
        self.sortby = IntVar()
        _mag = ttk.Radiobutton(frame1, text = "Magnitude", variable = self.sortby, value = 0)
        _loc = ttk.Radiobutton(frame1, text = "Location", variable = self.sortby, value = 1)
        _dist = ttk.Radiobutton(frame1, text = "Distance", variable = self.sortby, value = 2)
        _mag.pack(anchor = 'w')
        _loc.pack(anchor = 'w')
        _dist.pack(anchor = 'w')
        self.sortby.set(0)

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
                start = timer()
                printResults(data, self.sortby)
                print ("Processed data in {:2.3f} seconds".format(timer() - start))
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
    return(numeral[0][1])

def format_place(place):

    _regions = ["Region", "Ocean", "Ridge", "Sea", "Passage", "Rise", "Gulf"]

    # If location contains any key word, reassemble into a single string
    # and return the string unmodified

    _new_list = place.capitalize().split()

    for word in _new_list:
        if word in _regions:
            return(' '.join(_new_list))
    '''
    for region in _regions:
        if region in _new_list:
            _new_list.append("***")
            return(' '.join(_new_list))
    '''

    # Since no key words were found, split original string into two separated by ','
    # and then return as a string but with words reversed so that most significant
    # geography is at the beginning of the string.

    _new_list = place.split(', ')
    _new_list.reverse()
    _new_list[0] = _new_list[0].title()

    return (', '.join(_new_list))

def printResults (data, sortby=0):

    results = {}                # Store event data of interest
    magData = []                # Store all event magnitudes
    _sort = sortby.get()        # Convert IntVar to int to index sort function

    # Use get_IP_geo() to dynamically determine my location using IP addr lookup

    my_geo = get_IP_geo()
    my_lat = float(my_geo['loc'][0])
    my_long = float(my_geo['loc'][1])

    # Load the raw quake string data into a new local dictionary

    quakes_json = json.loads(data.decode('utf-8'))

    if "title" in quakes_json["metadata"]:
        count = quakes_json["metadata"]["count"]
        print ('Recorded total of {} events from {}'.format(count, quakes_json["metadata"]["title"]))

    # For each event, calculate distance from my coordinates.
    # Build a new dictionary structure containing just event data of interest:
    # results = {id : (magnitude, place, distance)}

    for e in quakes_json["features"]:
        long = e["geometry"]["coordinates"][0]
        lat  = e["geometry"]["coordinates"][1]
        distance = dist(lat, long, my_lat, my_long)

        if _sort == 1:
            place = format_place(e['properties']['place'])
        else:
            place = e['properties']['place']

        results.update({e['id']:[e['properties']['mag'], place, distance]})
        magData.append(e['properties']['mag'])

    # Output Statistical Analysis of Magnitude data

    print('\n{:*^85}\n'.format(' [Event statistical Analysis] '))

    header = 'Magnitude Max = {:2.2f}, Mean = {:2.2f}, Median = {:2.2f}, Mode = {:2.2f}' \
        .format(max(magData), mean(magData), median(magData), unique_mode(magData))

    print('{:^85}'.format(header))

    # Output Individual Event data sorted as determined by _sort variable

    if (_sort == 0):
        header = ' [Individual events sorted by MAGNITUDE] '
    elif (_sort == 1):
        header = ' [Individual events sorted by LOCATION] '
    elif (_sort == 2):
        header = ' [Events sorted by DISTANCE from: {} : {}] '.format(my_lat, my_long)
    else:
        header = ' [Have no idea how we are sorting] '

    print('\n{:*^79}\n'.format(header))

    for event_id in sorted(results.items(), key=lambda kv: kv[1][_sort]):
        print('{:4.2f} centered {:45.44} distance: {:>8.2f} miles'.format(
           (event_id[1][0]), event_id[1][1], (event_id[1][2])))

def main():
    root = Tk()
    USGS_Gui(root)
    root.mainloop()

if __name__ == "__main__": main()
