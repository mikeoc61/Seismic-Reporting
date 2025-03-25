from __future__ import print_function
import json
import datetime
from timeit import default_timer as timer

from IP_geo import get_IP_geo
from haversine import calc_dist as dist
from statistics import mean, median

__author__    = "Michael E. O'Connor"
__copyright__ = "Copyright 2018"


# This function returns the most commonly occurring numerical value when no single mode value exists
def unique_mode(a_list):
    numeral=[[a_list.count(n), n] for n in a_list]
    numeral.sort(key=lambda x:x[0], reverse=True)
    #print(numeral)
    return(numeral[0][1])

# Check argument type and force INT to FLOAT or return 0.00 if val type isn't either
def check_type(val):
    if isinstance(val, float) or isinstance(val, int) :
        return float(val)
    else:
        return 0.00

def format_place(place):

    _regions = ["Region", "Ocean", "Ridge", "Sea", "Passage", "Rise", "Gulf"]

    # If location contains any key word, reassemble into a single string
    # and return the string unmodified

    _new_list = place.capitalize().split()

    for word in _new_list:
        if word in _regions:
            return(' '.join(_new_list))

    # Since no key words were found, split original string into two separated by ','
    # and then return as a string but with words reversed so that most significant
    # geography is at the beginning of the string.

    _new_list = place.split(', ')
    _new_list.reverse()
    _new_list[0] = _new_list[0].title()

    return (', '.join(_new_list))

def printResults (data, sortby=0, rev_order=False, width=10):

    results = {}                # Store event data of interest
    magData = []                # Store all event magnitudes
    _sort = sortby.get()        # Convert IntVar to int to index sort function
    start = timer()             # Start timer to measure elapsed time

    # Use get_IP_geo() to dynamically determine my location using IP addr lookup

    my_geo = get_IP_geo()
    my_lat = float(my_geo['loc'][0])
    my_long = float(my_geo['loc'][1])
    my_city = my_geo['city']
    my_region = my_geo['region']

    # Load the raw quake string data into a new local dictionary

    quakes_json = json.loads(data.decode('utf-8'))

    # For each event, calculate distance from my coordinates.
    # Build a new dictionary structure containing just event data of interest:
    # results = {id : (magnitude, place, distance, time)}

    for e in quakes_json["features"]:
        long = e["geometry"]["coordinates"][0]
        lat  = e["geometry"]["coordinates"][1]
        distance = dist(lat, long, my_lat, my_long)
        seconds_since_epoch = e["properties"]["time"] / 1000.0

        if _sort == 1:
            place = format_place(e['properties']['place'])
        else:
            place = e['properties']['place']

        results.update({e['id']:[check_type(e['properties']['mag']), place, distance, seconds_since_epoch]})
        magData.append(check_type(e['properties']['mag']))

    # Output Header & Statistical Analysis of Magnitude data

    count = quakes_json["metadata"]["count"]
    e_time = timer() - start

    header = 'Recorded ' + str(count) + ' events from ' + quakes_json["metadata"]["title"]
    if len(magData):
        stats = 'Magnitude Max = {:2.2f}, Mean = {:2.2f}, Median = {:2.2f}, Mode = {:2.2f}' \
        .format(max(magData), mean(magData), median(magData), unique_mode(magData))
    else:
        stats = '** No results found. Try reducing Magnitude or increasing Time Period **'
    effort = 'Total processing time: {:2.2f} seconds'.format(e_time)
    
    print('{:*^{}}\n'.format(' [Event statistical Analysis] ', width))
    print ('{:^{}}\n'.format (header, width))
    print('{:^{}}\n'.format(stats, width))
    print('{:^{}}'.format(effort, width))

    # Output Individual Event data sorted as determined by _sort variable

    if (_sort == 0):
        header = ' [Events are sorted by MAGNITUDE] '
    elif (_sort == 1):
        header = ' [Events are sorted by LOCATION] '
    elif (_sort == 2):
        header = ' [Events are sorted by DISTANCE from: {}, {}] '.format(my_city, my_region)
    elif (_sort == 3):
        header = ' [Events are sorted by DATE & TIME] '
    else:
        header = ' [Have no idea how we are sorting] '

    print('\n{:*^{}}\n'.format(header, width))

    # iterate through sorted results and sent to stdout. Note have to use the .get method for 
    # reverse variable value to ensure that we have a true boolean value as tkinter BooleanVar is
    # interpreted differently.
    for event_id in sorted(results.items(), key=lambda kv: kv[1][_sort], reverse=rev_order.get()):
        dt = datetime.datetime.fromtimestamp(event_id[1][3])
        ds = dt.strftime("%H:%M:%S on %m/%d")
        mag = event_id[1][0]
        loc = event_id[1][1]
        distance = event_id[1][2]
        if mag >= 0.0:
            print('{:4.2f} centered {:46.45} distance: {:>8.2f} miles at {}'.format(mag, loc, distance, ds))