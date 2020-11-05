from sys import exit
import tkinter as tk
from tkinter import filedialog
import copy
from GpsPoint import GpsPoint
import folium


from Navigation import Navigation
from Header import Header

# Popup to select input station_data.sql file
root = tk.Tk()
root.withdraw()
log_file_name = "tmp.up"
# log_file_name = filedialog.askopenfilename()
# if not log_file_name:
#     print("Error: must select an asdo.log file")
#     exit(1)
print("Reading data from {}".format(log_file_name))

# Create a basemap centred somewhere around East Anglia
gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)

# Open station_data.sql file for parsing
# data_file = "/Users/Nathan/PycharmProjects/stationplotter/stadler_station_data.sql"
import re
log_file = open(log_file_name, 'r')

gps_previous = GpsPoint('', 0, 0, 0, 0)
gps_point = GpsPoint('', 0, 0, 0, 0)

# ip_addr = "10.177.156.21"
ip_addr = "10.182.144.21"

i_marker_count = [0]
i_map_count = 1
i_line = 0
for line in log_file:
    i_line += 1

    if not line.find(ip_addr) != 1:
        continue

    header = Header()
    line = header.stripHeader(line)

    if header.service == 'Navigation':
        navigation = Navigation(gps_map, gps_previous)
        navigation.parseLine(line, i_marker_count)

    # Update the map
    if i_marker_count[0] > 50:
        i_marker_count[0] = 0
        map_file = log_file_name + "." + str(i_map_count) + ".map.html"
        print("Writing to file {}".format(map_file))
        gps_map.location = [gps_point.lat, gps_point.lon]
        gps_map.save(map_file)
        gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)
        i_map_count += 1

map_file = log_file_name + "." + str(i_map_count) + ".map.html"
print("Writing to file {}".format(map_file))
gps_map.location = [gps_point.lat, gps_point.lon]
gps_map.save(map_file)
gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)

print("*** DONE ***")

