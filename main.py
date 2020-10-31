from sys import exit
import tkinter as tk
from tkinter import filedialog
import random

# Popup to select input station_data.sql file
root = tk.Tk()
root.withdraw()
log_file_name = "asdo.log.10"
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
for line in log_file:
    RADIUS = 10000
    circle_colours = ['#00ae53', '#86dc76', '#daf8aa', '#ffe6a4', '#ff9a61', '#ee0028']
    icon_colours = ['darkpurple', 'lightred', 'gray', 'black', 'blue', 'orange', 'beige',
                    'cadetblue', 'darkred', 'red', 'lightblue', 'white', 'purple',
                    'lightgreen', 'darkblue', 'lightgray', 'darkgreen', 'green', 'pink']

    # Regex for the DataFrame columns

    # 2020/10/28 16:01:52.270464120 NavMan: 420.Car-A is DISCONNECTED at ( GPS+Odo, 52.4192, 0.745005, 0, 0.141 )

    # gps_line_re = re.compile(".*NavMan.*\((?P<confidence>.*?),(?P<lat>[^,]+),(?P<lon>[^,]+)")
    gps_line_re = re.compile(".*Publishing NavigationMessage\((?P<lat>[^,]+),(?P<lon>[^,]+),(?P<gpsSpeed>[^,]+),(?P<confidence>.*?)")
    match = gps_line_re.search(line)
    if match:
        gps_d = match.groupdict()
        print (gps_d)
        continue

        # Add markers to the map
        lat = gps_d["lat"]
        lon=  gps_d["lon"]
        confidence = gps_d["confidence"].lower().strip()

        if confidence == 'gps':
            icon_colour = 'green'
        elif confidence == 'gps+odo':
            icon_colour = 'orange'
        elif confidence == 'odo':
            icon_colour = 'red'
        else:
            print ("Can't match confidence: ", confidence.lower())
            continue


        folium.Marker(location=[lat, lon],
                      popup = gps_d,
                      icon=folium.Icon(icon_colour, icon='cloud')).\
            add_to(gps_map)


        folium.Circle([lat, lon],
                      radius=RADIUS, fill=True,
                      fill_color=random.choice(circle_colours),
                      fill_opacity=0.25,
                      tooltip=confidence).\
            add_to(gps_map)

map_file = log_file_name + ".map.html"
print("Writing to file {}".format(map_file))
gps_map.save(map_file)

