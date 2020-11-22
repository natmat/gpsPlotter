from sys import exit
import tkinter as tk
from tkinter import filedialog
from GpsPoint import GpsPoint
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

log_file = open(log_file_name, 'r')

gps_previous = GpsPoint('', 0, 0, 0, 0)
gps_point = GpsPoint('', 0, 0, 0, 0)
mapping = Mapping(log_file_name)

# ip_addr = "10.177.156.21"
# ip_addr = "10.182.144.21"
# ip_addr = "10.181.72.21"
# ip_addr = "10.176.36.21"
ip_addr = None

marker_count = [0]
map_count = 1
i_line = 0
header = Header()

# navigation = Navigation(0, 0, 0, '', 0)
# navigation.setGpsPoint(gps_map, gps_point, gps_previous)
nav_msg = Navigation()

for line in log_file:
    i_line += 1

    if ip_addr is not None:
        if line.find(ip_addr) == -1:
            continue

    try:
        data = header.stripHeader(line)
    except:
        print("ERROR: {}\n\t >>> {}\n\t ### {} ".format(i_line, line, data))
        continue

    # print(line)
    if ip_addr is None:
        answer = input("Filter on " + header.ip_addr + "? [y]")
        if answer[:1].lower() == 'y':
            ip_addr = header.ip_addr

    if header.service == 'Navigation':
        if line.find('NavigationMessage') == -1:
            continue
        Navigation.newNavigationMessage(nav_msg, data)
        mapping.plot_nav_msg(nav_msg, header)

    if mapping.draw_map(header.hours):
        del mapping
        mapping = Mapping(log_file_name)
        nav_msg_prev = None

# Draw remaining markers
mapping.draw_map(header.hours)
mapping.save_map_file()

print("*** DONE ***")
