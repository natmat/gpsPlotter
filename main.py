from sys import exit
import copy
import tkinter as tk
from tkinter import filedialog
from GpsPoint import GpsPoint
import folium
import sys
from Header import Header
from Mapping import Mapping
from Navigation import Navigation

# Popup to select input station_data.sql file
root = tk.Tk()
root.withdraw()
# log_file_name = "small.down"
log_file_name = filedialog.askopenfilename()
if not log_file_name:
    print("Error: must select an asdo.log file")
    exit(1)
print("Reading data from {}".format(log_file_name))

# Open station_data.sql file for parsing
# data_file = "/Users/Nathan/PycharmProjects/stationplotter/stadler_station_data.sql"
import re

log_file = open(log_file_name, 'r')

gps_previous = GpsPoint('', 0, 0, 0, 0)
gps_point = GpsPoint('', 0, 0, 0, 0)
mapping = Mapping(log_file_name)

# ip_addr = "10.177.156.21"
ip_addr = "10.182.144.21"
ip_addr = "10.181.72.21"

marker_count = [0]
map_count = 1
i_line = 0

# navigation = Navigation(0, 0, 0, '', 0)
# navigation.setGpsPoint(gps_map, gps_point, gps_previous)
nav_msg = Navigation()

for line in log_file:
    # print(line)
    i_line += 1

    if not line.find(ip_addr) != 1:
        continue

    header = Header()
    try:
        line = header.stripHeader(line)
    except:  # catch *all* exceptions
        continue
    # print("{}: {}".format(i_line, line))

    if header.service == 'Navigation':
        Navigation.newNavigationMessage(nav_msg, line)
        # print(nav_msg.lat, nav_msg.lon, nav_msg.dist, nav_msg.confidence, nav_msg.gps_speed)
    else:
        # print("Unknown service: {}".format(header.service))
        continue

    mapping.plot_nav_msg(nav_msg, header)

    if mapping.draw_map(header.hours):
        del mapping
        mapping = Mapping(log_file_name)
        nav_msg_prev = None

# Draw remaining markers
mapping.draw_map(header.hours)
mapping.save_map_file()

print("*** DONE ***")
