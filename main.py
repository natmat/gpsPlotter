from sys import exit
import tkinter as tk
from tkinter import filedialog
import copy

# Popup to select input station_data.sql file
root = tk.Tk()
root.withdraw()
log_file_name = "tmp"
# log_file_name = filedialog.askopenfilename()
# if not log_file_name:
#     print("Error: must select an asdo.log file")
#     exit(1)
print("Reading data from {}".format(log_file_name))

# Set up the DataFrame for the oolumns to extract from the station_data.sql waypoint table data
import pandas as pd
df = pd.DataFrame(columns=['waypoint_name', 'waypoint_type', 'waypoint_id', 'waypoint_lat', 'waypoint_long', 'waypoint_radius', 'tap_tsi_code'])

# Create a basemap centred somewhere around East Anglia
import folium
# gps_map = folium.Map(location=[51.648611, -0.052778], zoom_start=10, tiles="CartoDB dark_matter")
gps_map = folium.Map(location=[51.648611, -0.052778], zoom_start=10)

# Open station_data.sql file for parsing
# data_file = "/Users/Nathan/PycharmProjects/stationplotter/stadler_station_data.sql"
import re
log_file = open(log_file_name, 'r')

RADIUS = 10000
icon_colours = ['darkpurple', 'lightred', 'gray', 'black', 'blue', 'orange', 'beige',
                'cadetblue', 'darkred', 'red', 'lightblue', 'white', 'purple',
                'lightgreen', 'darkblue', 'lightgray', 'darkgreen', 'green', 'pink']

class GpsPoint:
  def __init__(self, confidence, lat, lon, dist):
    self.confidence = [] if confidence is None else confidence
    self.lat = [] if lat is None else lat
    self.lon = [] if lon is None else lon
    self.dist = [] if dist is None else dist

    def __init__(self, d):
        self.confidence = d["confidence"].lower().strip()
        self.lat = d["lat"]
        self.lon = d["lon"]
        self.dist = d["dist"]

gps_previous = GpsPoint('', 0, 0, 0)
gps_point = GpsPoint('', 0, 0, 0)

for line in log_file:
    # Regex for gps data
    # gps_line_re = re.compile(".*NavMan.*\((?P<confidence>.*?),(?P<lat>[^,]+),(?P<lon>[^,]+)")
    gps_line_re = re.compile(".*Publishing NavigationMessage\((?P<lat>[^,]+),(?P<lon>[^,]+),(?P<dist>[^,]+),"
                             "(?P<confidence>.*?),.*")
    match = gps_line_re.search(line)
    if match:
        gps_d = match.groupdict()
        print (gps_d)

        # Add markers to the map
        gps_point.confidence = gps_d["confidence"].lower().strip()
        gps_point.lat = gps_d["lat"]
        gps_point.lon = gps_d["lon"]
        gps_point.dist = gps_d["dist"]

        # ignore if no change in conf
        if (gps_point.confidence == 'high' and gps_point.confidence == gps_previous.confidence):
            if not i_repeat % 20:
                folium.CircleMarker(location=[gps_point.lat, gps_point.lon],
                                    popup = gps_d,
                                    color=icon_colour,
                                    radius=10,
                                    fill=True).\
                    add_to(gps_map)
            i_repeat += 1
            continue

        i_repeat = 0
        draw_marker = True
        if gps_point.confidence == 'high':
            icon_colour = 'green'
        elif gps_point.confidence == 'medium':
            icon_colour = 'orange'
        elif gps_point.confidence == 'low':
            draw_marker = False
            icon_colour = 'purple'
            #Draw increase circles
            low_radius = int(gps_point.dist) - int(gps_previous.dist)
            folium.Circle([gps_previous.lat, gps_previous.lon],
                             radius=low_radius,
                             fill=False,
                             color=icon_colour,
                             tooltip=str(low_radius)).\
                add_to(gps_map)
        else:
            #error (or other?)
            draw_marker = False
            icon_colour = 'red'
            folium.Circle([gps_point.lat, gps_point.lon],
                          radius=200,
                          fill=False,
                          color=icon_colour,
                          tooltip=gps_d).\
                add_to(gps_map)

        if draw_marker:
            folium.Marker(location=[gps_point.lat, gps_point.lon],
                          popup = gps_d,
                          icon=folium.Icon(icon_colour)).\
                add_to(gps_map)

            # save current to previous
            gps_previous = copy.deepcopy(gps_point)

map_file = log_file_name + ".map.html"
print("Writing to file {}".format(map_file))
gps_map.save(map_file)
print("*** DONE ***")

