from sys import exit
import tkinter as tk
from tkinter import filedialog
import copy

import gpsPoint

# Popup to select input station_data.sql file
root = tk.Tk()
root.withdraw()
log_file_name = "tmp.down"
# log_file_name = filedialog.askopenfilename()
# if not log_file_name:
#     print("Error: must select an asdo.log file")
#     exit(1)
print("Reading data from {}".format(log_file_name))

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



gps_previous = gpsPoint.GpsPoint('', 0, 0, 0, 0)
gps_point = gpsPoint.GpsPoint('', 0, 0, 0, 0)

for line in log_file:
    # Regex for gps data
    # 2020/10/29 07:25:46.890862914 10.177.156.21 AUD Navigation Navigation.cpp@325: Publishing NavigationMessage( 52.6252, 1.30934, 700, HIGH, 0.033 )
    # gps_line_re = re.compile(".*NavMan.*\((?P<confidence>.*?),(?P<lat>[^,]+),(?P<lon>[^,]+)")
    gps_line_re = re.compile(".*Publishing NavigationMessage\("
                             "(?P<lat>[^,]+),\s*(?P<lon>[^,]+),\s*(?P<dist>\d+),\s*"
                             "(?P<confidence>[^,]+),\s*"
                             "(?P<gpsSpeed>[^\s]+)"
                             ".*")
    match = gps_line_re.search(line)
    if match:
        gps_d = match.groupdict()
        # print(gps_d)

        # Add markers to the map
        gps_point.confidence = gps_d["confidence"].lower().strip()
        gps_point.lat = gps_d["lat"]
        gps_point.lon = gps_d["lon"]
        gps_point.dist = gps_d["dist"]
        gps_point.gpsSpeed = gps_d["gpsSpeed"]

        # ignore if no change in conf
        if (gps_point.confidence == 'high' and gps_point.confidence == gps_previous.confidence):
            gps_previous = copy.deepcopy(gps_point)
            if not i_repeat % 20:
                # print(gps_d)
                speed_radius = float(gps_point.gpsSpeed)/10
                folium.CircleMarker(location=[gps_point.lat, gps_point.lon],
                                    popup = gps_d,
                                    color=icon_colour,
                                    radius=speed_radius,
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
            print(gps_d)
            draw_marker = True
            icon_colour = 'red'
            # Copy previous lat/long, but retain confidence
            confidence = gps_point.confidence
            gps_point = copy.deepcopy(gps_previous)
            gps_point.confidence = confidence
            folium.Circle([gps_point.lat, gps_point.lon],
                          radius=2000,
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

