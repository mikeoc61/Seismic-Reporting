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

        style = ttk.Style(master)
        style.theme_use('aqua')

        master.title('USGS Earthquake Data, Magnitude >= 2.5')
        frame0 = ttk.Panedwindow(master, orient = HORIZONTAL)
        frame0.pack(fill = BOTH, expand = False)
        frame1 = ttk.Frame(frame0, width = 100, height = 300, relief = SUNKEN)
        frame2 = ttk.Frame(frame0, width = 500, height = 300, relief = SUNKEN)
        frame0.add(frame1, weight = 1)
        frame0.add(frame2, weight = 4)
        ttk.Label(frame1, text = "Select sample period", justify = LEFT).pack(padx=(5,5))

        # Radio Buttons used to select time period

        self.period = StringVar()
        day = ttk.Radiobutton(frame1, text = "Past 24 hrs", variable = self.period, value = "day")
        week = ttk.Radiobutton(frame1, text = "Past Week", variable = self.period, value = "week")
        month = ttk.Radiobutton(frame1, text = "Past Month", variable = self.period, value = "month")
        self.period.set("day")
        day.pack(anchor = 'w')
        week.pack(anchor = 'w')
        month.pack(anchor = 'w')

        # Button pressed to generate Results

        result_button = ttk.Button(frame1)
        result_button.config(text = "Get Results", command = self.submit)
        result_button.pack(anchor = 's', pady=(10, 10))

        # Text Box used to store and scroll output if applicable

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
            if (webUrl.getcode() == 200):
                data = webUrl.read()
                sys.stdout.write = redirector
                print ("From: {}".format(quakeData))
                printResults(data)
            else:
                print ("Can't retrieve quake data " + str(webUrl.getcode()))
        except:
            print ("Fatal error opening: {}".format(quakeData))
            raise SystemExit()

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
