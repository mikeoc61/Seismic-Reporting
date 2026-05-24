#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
+---------------------------------------------------------------------
+ Query, sort, format and output USGS earthquate data
+
+ GeoJSON is a format for encoding a variety of geographic data structures. 
+ A GeoJSON object may represent a geometry, a feature, or a collection of features. 
+ GeoJSON uses the JSON standard.
+
+ See the GeoJSON site for more information: http://www.geojson.org/
+
+ Uses Tkinter (tcl/tk) to provide GUI
+
+ See: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
+---------------------------------------------------------------------
'''

__author__ = 'Michael E. OConnor'
__copyright__ = 'Copyright 2023'

import sys
from tkinter import *
from tkinter import ttk
from output import printResults
from urllib.request import urlopen

if sys.version_info <= (3, 0):
    print("Sorry, {} requires Python 3.x, detected version: {}".format \
          (sys.argv[0], str(sys.version_info[0]) + '.' + str(sys.version_info[1])))
    raise SystemExit()

# URL Base for earthquake data feed. Will be appended to in USGS_Gui class

quake_URL_base = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"

# Initialization function for the GUI using Tcl/Tk
class USGS_Gui:

    MASTER_WIDTH = 106      # Width of GUI display window in character count
    MASTER_HEIGHT = 40      # Heigth of GUI display frame in character count
    SIDE_WIDTH = 100        # Width of left panel
    WIDTH = 500             # Width of Result frame in pixels
    HEIGHT = 300            # Heigth of result frame in pixels

    def __init__(self, master):

        master.title('USGS Earthquake Data')
        frame0 = ttk.Panedwindow(master, orient=HORIZONTAL)
        frame0.pack(fill=BOTH, expand=True)
        # Creating two frames within the window
        frame1 = ttk.Frame(frame0, width=self.SIDE_WIDTH, height=self.HEIGHT, relief=RAISED, padding=10)
        frame2 = ttk.Frame(frame0, width=self.WIDTH, height=self.HEIGHT, relief=SUNKEN)
        frame0.add(frame1, weight=1)
        frame0.add(frame2, weight=4)
        
        self.style = ttk.Style()
        self.style.theme_use('aqua')
        self.style.configure('TButton', font='Arial 15', relief="flat")

        # Add labels and radio buttons for selecting the sample period
        self.add_label(frame1, "Time Period")
        self.period = StringVar()
        self.add_radiobutton(frame1, "Past Hour", self.period, "hour")
        self.add_radiobutton(frame1, "Past Day", self.period, "day")
        self.add_radiobutton(frame1, "Past Week", self.period, "week")
        self.add_radiobutton(frame1, "Past Month", self.period, "month")
        self.period.set("day")

        # Add labels and radio buttons for selecting the Magnitude range
        self.add_label(frame1, "Magnitude")
        self.mag = StringVar()
        self.add_radiobutton(frame1, "Significant", self.mag, 'significant')
        self.add_radiobutton(frame1, "M4.5+", self.mag, '4.5')
        self.add_radiobutton(frame1, "M2.5+", self.mag, '2.5')
        self.add_radiobutton(frame1, "M1.0+", self.mag, '1.0')
        self.add_radiobutton(frame1, "All Quakes", self.mag, 'all')
        self.mag.set("1.0")

        # Add labels and radio buttons for selecting the sorting method
        self.add_label(frame1, "Sort By")
        self.sortby = IntVar()
        self.add_radiobutton(frame1, "Magnitude", self.sortby, 0)
        self.add_radiobutton(frame1, "Location", self.sortby, 1)
        self.add_radiobutton(frame1, "Distance", self.sortby, 2)
        self.add_radiobutton(frame1, "Time", self.sortby, 3)
        self.sortby.set(0)

        # Add labels and radio buttons for selecting the sort order
        self.add_label(frame1, "Sort Order")
        self.reverse = BooleanVar()
        self.add_radiobutton(frame1, "Ascending", self.reverse, False)
        self.add_radiobutton(frame1, "Descending", self.reverse, True)
        self.reverse.set(False)

        # Add dividing line between radio buttons and submit button
        self.add_line(frame1, 'white')

        # Add a button to submit the selected options
        result_button = Button(frame1, text="Get Results", command=self.submit, bg='white', fg='blue', relief='sunken')
        result_button.pack(anchor='s', pady=3)

        # Add a text box to display the results
        self.result_box = Text(frame2, width=self.MASTER_WIDTH, height=self.MASTER_HEIGHT)
        scrollbar = Scrollbar(frame2, orient=VERTICAL, command=self.result_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result_box["yscrollcommand"] = scrollbar.set
        self.result_box.pack(side=LEFT, fill=BOTH, expand=YES)

    # Function to add a tk style label to a frame and set default colors, relief style and vertical padding
    def add_label(self, frame, text):
        Label(frame, text=text, bg="blue", fg="white", relief='ridge', justify=LEFT).pack(fill=X, pady=5)

    # Function to add a ttk style radio button to a frame and set default vertical padding
    def add_radiobutton(self, frame, text, variable, value):
        ttk.Radiobutton(frame, text=text, variable=variable, value=value).pack(anchor='w', pady=1)

    # Create a vertical canvas and draw a dividing line
    # Parameters are: canvas.create_line(x1, y1, x2, y2, options)
    def add_line(self, frame, color):
        canvas = Canvas(frame, width=self.SIDE_WIDTH, height=8)
        canvas.pack()
        canvas.create_line(0, 8, self.SIDE_WIDTH, 8, fill=color)

    # Function to submit the selected options
    def submit(self):
        self.clear()
        quakeData = quake_URL_base + self.mag.get() + "_" + self.period.get() + ".geojson"
        try:
            webUrl = urlopen (quakeData)
        except:
            print("Fatal error opening: {}".format(quakeData))
            raise SystemExit()
        else:
            if (webUrl.getcode() == 200):
                data = webUrl.read()
                sys.stdout.write = self.redirector
                printResults(data, self.sortby, self.reverse, self.MASTER_WIDTH)
                sys.stdout.write = sys.__stdout__
            else:
                print("Can't retrieve quake data " + str(webUrl.getcode()))

    # Function to clear the results
    def clear(self):
        self.result_box.delete(1.0, 'end')

    # Function to redirect the output to the GUI text box
    def redirector(self, inputStr):
        self.result_box.insert(INSERT, inputStr)

def main():

    root = Tk()
    USGS_Gui(root)
    root.mainloop()

if __name__ == "__main__":
    main()