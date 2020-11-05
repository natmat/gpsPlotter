import re
from GpsPoint import GpsPoint
import folium
import copy

class Navigation():
    def __init__(self, gps_map, gps_previous):
        self.gps_map = gps_map
        self.gps_point = None
        self.gps_previous = gps_previous

    def parseLine(self, line, i_marker_count):
        # gps_line_re = re.compile(".*NavMan.*\((?P<confidence>.*?),(?P<lat>[^,]+),(?P<lon>[^,]+)")
        line_re = re.compile(".*Publishing NavigationMessage\("
                                 "(?P<lat>[^,]+),\s*(?P<lon>[^,]+),\s*(?P<dist>\d+),\s*"
                                 "(?P<confidence>[^,]+),\s*"
                                 "(?P<gpsSpeed>[^\s]+)"
                                 ".*")
        match = line_re.search(line)
        if match:
            gps_d = match.groupdict()

            # Add markers to the map
            self.gps_point = GpsPoint(gps_d["confidence"].lower().strip(),
                                      gps_d["lat"],
                                      gps_d["lon"],
                                      gps_d["dist"],
                                      gps_d["gpsSpeed"])

            # Are we now in low speed (<1kph)?
            if (float(self.gps_point.dist) < 1.0 and float(self.gps_previous.dist) >= 1.0):
                i_marker_count[0] += 1
                folium.Circle([self.gps_point.lat, self.gps_point.lon],
                              radius=200,
                              fill=False,
                              color='blue',
                              tooltip=gps_d).\
                    add_to(gps_map)
                return

            # If were HIGH ocnf and stil HIGH, then only map every N samples
            if (self.gps_point.confidence == 'high' and self.gps_point.confidence == self.gps_previous.confidence):
                gps_previous = copy.deepcopy(self.gps_point)
                if not i_repeat % 50:
                    i_marker_count[0] += 1
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
                return

            # Will not update map for conf levels.
            i_repeat = 0
            draw_marker = True
            if self.gps_point.confidence == 'high':
                icon_colour = 'green'
            elif self.gps_point.confidence == 'medium':
                icon_colour = 'orange'
            elif self.gps_point.confidence == 'low':
                draw_marker = False
                icon_colour = 'purple'
                low_radius = int(self.gps_point.dist) - int(self.gps_previous.dist)
                #Draw circles with increasing radius (of distance travelled)
                i_marker_count[0] += 1
                folium.Circle([self.gps_previous.lat, self.gps_previous.lon],
                              radius=low_radius,
                              fill=False,
                              color=icon_colour,
                              tooltip=str(low_radius)).\
                    add_to(self.gps_map)
            else:
                #error (or other?)
                # Don't map consecutive errors
                if self.gps_previous.confidence == 'error':
                    return

                draw_marker = True
                icon_colour = 'red'
                # Copy previous lat/long, but retain confidence
                confidence = self.gps_point.confidence
                self.gps_point = copy.deepcopy(self.gps_previous)
                self.gps_point.confidence = confidence
                i_marker_count[0] += 1
                folium.Circle([self.gps_point.lat, self.gps_point.lon],
                              radius=500,
                              fill=False,
                              color=icon_colour,
                              tooltip=gps_d).\
                    add_to(self.gps_map)

            if draw_marker:
                i_marker_count[0] += 1
                folium.Marker(location=[self.gps_point.lat, self.gps_point.lon],
                              popup=gps_d,
                              icon=folium.Icon(icon_colour)).\
                    add_to(self.gps_map)

                # save current to previous
                gps_previous = copy.deepcopy(self.gps_point)
