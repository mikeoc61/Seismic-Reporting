from __future__ import print_function
import json

from IP_geo import get_IP_geo
from haversine import calc_dist as dist
from statistics import mean, mode, median

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"

# Return largest, most commonly occuring numerical value when no single mode
# value exists. Statistics.mode() throws an exception when there is no single
# unique mode value

def unique_mode(a_list):
    numeral=[[a_list.count(n), n] for n in a_list]
    numeral.sort(key=lambda x:x[0], reverse=True)
    #print(numeral)
    return(numeral[0][1])

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
        count = quakes_json["metadata"]["count"];
        print ('Recorded total of {} events from {}'.format(count, quakes_json["metadata"]["title"]))

    # For each event, calculate distance from my coordinates.
    # Build a new dictionary structure containing just event data of interest:
    # results = {id : (magnitude, location, distance)}

    for e in quakes_json["features"]:
        long = e["geometry"]["coordinates"][0]
        lat  = e["geometry"]["coordinates"][1]
        distance = dist(lat, long, my_lat, my_long)
        results.update({e['id']:[e['properties']['mag'], e['properties']['place'], distance]})
        magData.append(e['properties']['mag'])

    # Output Statistical Analysis of Magnitude data

    print('\n{:*^79}\n'.format(' [Event statistical Analysis] '))

    header = 'Magnitude Max = {:2.2f}, Mean = {:2.2f}, Median = {:2.2f}, Mode = {:2.2f}' \
        .format(max(magData), mean(magData), median(magData), unique_mode(magData))

    print('{:^79}'.format(header))

    # Output Individual Event data sorted as determined by _sort variable

    if (_sort == 2):
        header = ' [Individual events sorted nearest to: {} : {}] '.format(my_lat, my_long)
    elif (_sort == 0):
        header = ' [Individual events sorted by magnitude] '
    else:
        header = ' [Have no idea how we are sorting - expected 0 or 2]'

    print('\n{:*^79}\n'.format(header))

    for id in sorted(results.items(), key=lambda kv: kv[1][_sort]):
        print('{:4.2f} centered {:40.39} distance: {:>8.2f} miles'.format(
           (id[1][0]), id[1][1], (id[1][2])))
