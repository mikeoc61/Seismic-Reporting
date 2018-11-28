#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+---------------------------------------------------------------------
+ Query, sort, format and output USGS earthquate data
+
+ Uses Tkinter (tcl/tk) to provide GUI
+
+ See: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
+
+ for info on request options and data formats
+---------------------------------------------------------------------
'''

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

import sys
from tkinter import *
from tkinter import ttk
from output import printResults
from timeit import default_timer as timer

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected version: {}".format \
          (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()
else:
    from urllib.request import urlopen

# URL Base for earthquake data feed. Will be appended to in USGS_Gui class

quake_URL_base = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"

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

        result_box = Text(frame2, width=85, height=20)
        scrollbar = Scrollbar(frame2, orient=VERTICAL, command=result_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        result_box["yscrollcommand"]=scrollbar.set
        result_box.pack(side=LEFT, fill=BOTH, expand = YES)

    def submit(self):

        self.clear()

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

def main():

    root = Tk()
    USGS_Gui(root)
    root.mainloop()

if __name__ == "__main__": main()
