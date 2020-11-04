import re

class Navigation():
    def __init__(self):
        self.self.gps_point = None
        print('ctor')

    def parseLine(self, line):
        # gps_line_re = re.compile(".*NavMan.*\((?P<confidence>.*?),(?P<lat>[^,]+),(?P<lon>[^,]+)")
        line_re = re.compile(".*Publishing NavigationMessage\("
                                 "(?P<lat>[^,]+),\s*(?P<lon>[^,]+),\s*(?P<dist>\d+),\s*"
                                 "(?P<confidence>[^,]+),\s*"
                                 "(?P<gpsSpeed>[^\s]+)"
                                 ".*")
        match = line_re.search(line)
        if match:
            gps_d = match.groupdict()
            # print(gps_d)

            # Add markers to the map
            self.self.gps_point.confidence = gps_d["confidence"].lower().strip()
            self.gps_point.lat = gps_d["lat"]
            self.gps_point.lon = gps_d["lon"]
            self.gps_point.dist = gps_d["dist"]
            self.gps_point.gpsSpeed = gps_d["gpsSpeed"]

            # print("dist:", float(self.gps_point.dist))
            if (float(self.gps_point.dist) < 1.0 and float(gps_previous.dist) >= 1.0):
                i_marker_count += 1
                folium.Circle([self.gps_point.lat, self.gps_point.lon],
                              radius=200,
                              fill=False,
                              color='blue',
                              tooltip=gps_d).\
                    add_to(gps_map)

            # If still HIGH, then map every i_repeat
            if (self.gps_point.confidence == 'high' and self.gps_point.confidence == gps_previous.confidence):
                gps_previous = copy.deepcopy(self.gps_point)
                if not i_repeat % 50:
                    # print(gps_d)
                    i_marker_count += 1
                    speed_radius = float(self.gps_point.gpsSpeed)/5
                    tool_tip = header.hours + ":" + header.minutes
                    folium.CircleMarker(location=[self.gps_point.lat, self.gps_point.lon],
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
            if self.gps_point.confidence == 'high':
                icon_colour = 'green'
            elif self.gps_point.confidence == 'medium':
                icon_colour = 'orange'
            elif self.gps_point.confidence == 'low':
                draw_marker = False
                icon_colour = 'purple'
                low_radius = int(self.gps_point.dist) - int(gps_previous.dist)
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
                confidence = self.gps_point.confidence
                self.gps_point = copy.deepcopy(gps_previous)
                self.gps_point.confidence = confidence
                i_marker_count += 1
                folium.Circle([self.gps_point.lat, self.gps_point.lon],
                              radius=500,
                              fill=False,
                              color=icon_colour,
                              tooltip=gps_d).\
                    add_to(gps_map)

            if draw_marker:
                i_marker_count += 1
                folium.Marker(location=[self.gps_point.lat, self.gps_point.lon],
                              popup=gps_d,
                              icon=folium.Icon(icon_colour)).\
                    add_to(gps_map)

                # save current to previous
                gps_previous = copy.deepcopy(self.gps_point)

        if i_marker_count > 500:
            i_marker_count = 0
            map_file = log_file_name + "." + str(i_map_count) + ".map.html"
            print("Writing to file {}".format(map_file))
            gps_map.location = [self.gps_point.lat, self.gps_point.lon]
            gps_map.save(map_file)
            gps_map = folium.Map(location=[52.617, 1.3144], zoom_start=10)
            i_map_count += 1