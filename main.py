from sys import exit
import tkinter as tk
from tkinter import filedialog
import copy

import gpsPoint
import Header

# Popup to select input station_data.sql file
root = tk.Tk()
root.withdraw()
log_file_name = "test"
log_file_name = filedialog.askopenfilename()
if not log_file_name:
    print("Error: must select an asdo.log file")
    exit(1)
print("Reading data from {}".format(log_file_name))

# Create a basemap centred somewhere around East Anglia
import folium
gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)

# Open station_data.sql file for parsing
# data_file = "/Users/Nathan/PycharmProjects/stationplotter/stadler_station_data.sql"
import re
log_file = open(log_file_name, 'r')

gps_previous = gpsPoint.GpsPoint('', 0, 0, 0, 0)
gps_point = gpsPoint.GpsPoint('', 0, 0, 0, 0)

# ip_addr = "10.177.156.21"
ip_addr = "10.182.144.21"

i_marker_count = 0
i_map_count = 0
i_line = 0
for line in log_file:
    i_line += 1

    if not line.find(ip_addr) != 1:
        continue

    # Regex for gps data
    # 2020/10/29 07:25:46.890862914 10.177.156.21 AUD Navigation Navigation.cpp@325: Publishing NavigationMessage( 52.6252, 1.30934, 700, HIGH, 0.033 )
    header_re = re.compile("^(?P<date>[\d]{4}\/[\d]{2}\/[\d]{2})\s+"
                           "(?P<hours>[\d]{2}):(?P<minutes>[\d]{2}):(?P<seconds>[^,]+)\s+"
                           "(?P<ip_addr>[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})\s+"
                           "(?P<service>[\w]+)\s"
                           ".*")
    match = header_re.search(line)
    if match:
        header = Header.Header(match.groupdict())

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

        # print("dist:", float(gps_point.dist))
        if (float(gps_point.dist) < 1.0 and float(gps_previous.dist) >= 1.0):
            i_marker_count += 1
            folium.Circle([gps_point.lat, gps_point.lon],
                          radius=200,
                          fill=False,
                          color='blue',
                          tooltip=gps_d).\
                add_to(gps_map)

        # If still HIGH, then map every i_repeat
        if (gps_point.confidence == 'high' and gps_point.confidence == gps_previous.confidence):
            gps_previous = copy.deepcopy(gps_point)
            if not i_repeat % 50:
                # print(gps_d)
                i_marker_count += 1
                speed_radius = float(gps_point.gpsSpeed)/5
                tool_tip = header.hours + ":" + header.minutes
                folium.CircleMarker(location=[gps_point.lat, gps_point.lon],
                                    popup=gps_d,
                                    color=icon_colour,
                                    radius=speed_radius,
                                    tooltip=tool_tip,
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
            low_radius = int(gps_point.dist) - int(gps_previous.dist)
            #Draw circles with increasing radius (of distance travelled)
            i_marker_count += 1
            folium.Circle([gps_previous.lat, gps_previous.lon],
                          radius=low_radius,
                          fill=False,
                          color=icon_colour,
                          tooltip=str(low_radius)).\
                add_to(gps_map)
        else:
            #error (or other?)
            # print(gps_d)
            if gps_previous.confidence == 'error':
                continue
            draw_marker = True
            icon_colour = 'red'
            # Copy previous lat/long, but retain confidence
            confidence = gps_point.confidence
            gps_point = copy.deepcopy(gps_previous)
            gps_point.confidence = confidence
            i_marker_count += 1
            folium.Circle([gps_point.lat, gps_point.lon],
                          radius=500,
                          fill=False,
                          color=icon_colour,
                          tooltip=gps_d).\
                add_to(gps_map)

        if draw_marker:
            i_marker_count += 1
            folium.Marker(location=[gps_point.lat, gps_point.lon],
                          popup=gps_d,
                          icon=folium.Icon(icon_colour)).\
                add_to(gps_map)

            # save current to previous
            gps_previous = copy.deepcopy(gps_point)

    file_write = False
    if i_marker_count > 500:
        file_write = True
        i_marker_count = 0
        i_map_count += 1
        map_file = log_file_name + "." + str(i_map_count) + ".map.html"
        print("Writing to file {}".format(map_file))
        gps_map.location = [gps_point.lat, gps_point.lon]
        gps_map.save(map_file)
        gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)

if not file_write:
    map_file = log_file_name + ".map.html"
    print("Writing to file {}".format(map_file))
    gps_map.location = [gps_point.lat, gps_point.lon]
    gps_map.save(map_file)
    gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)

print("*** DONE ***")

