import copy
import folium
import re

from GpsPoint import GpsPoint
from operator import itemgetter


class Navigation:
    i_repeat = 0

    def __init__(self):
        self.lat = self.lon = 0
        self.dist = self.gps_speed = 0
        self.confidence = 'ERROR'

    def print_me(self):
        print("NavMsg: [{},{}]:{},{},{}".format(self.lat, self.lon, self.confidence, self.gps_speed, self.dist))

    @property
    def __repr__(self):
        return ("[{},{}]:{},{},{}".format(self.lat, self.lon, self.confidence, self.gps_speed, self.dist))

    def get_gps(self):
        return [self.lat, self.lon]

    def set_gps_point(self, gps_map, gps_point, gps_previous):
        self.gps_map = gps_map
        self.gps_point = gps_point
        self.gps_previous = gps_previous

    def usingGps(self):
        # Using some GPS
        return (self.gps_point.confidence == "high" and self.gps_point.confidence == "medium")

    def isStopped(self):
        return (float(self.gps_point.dist) < 1)

    def parseLine(self, line, header, i_marker_count):
        line_re = re.compile(".*Publishing NavigationMessage\("
                             "(?P<lat>[^,]+),\s*(?P<lon>[^,]+),\s*(?P<dist>\d+),\s*"
                             "(?P<confidence>[^,]+),\s*"
                             "(?P<gpsSpeed>[^\s]+)"
                             ".*")
        match = line_re.search(line)
        if match:
            gps_d = match.groupdict()

    @classmethod
    def newNavigationMessage(cls, nav_msg, line):
        if line.find("NavigationMessage") == -1:
            # Not found
            return None

        # Regex out the nav msg between '()' in the payload
        # ...NavigationMessage( 51.5219, -0.078844, 6144, MEDIUM, 8.365 )
        gps_data = re.sub(r'^.*\((.*)\).*', r'\1', line)
        split_line = [x.strip() for x in gps_data.split(',')]
        # print(split_line)

        # Instantiate the NavMsg
        nav_msg.lat, nav_msg.lon, nav_msg.dist, nav_msg.confidence, nav_msg.gps_speed \
            = itemgetter(0, 1, 2, 3, 4, )(split_line)
        nav_msg.confidence = nav_msg.confidence.lower()

        # Trial use of dict
        # dict_names = ['lat', 'lon', 'dist', 'confidence', 'gps_speed']
        # print(dict_names)
        # dict(zip(dict_names, split_line))

        return

        # line_re = re.compile(".*Publishing NavigationMessage\("
        #                      "(?P<lat>[^,]+),\s*(?P<lon>[^,]+),\s*(?P<dist>\d+),\s*"
        #                      "(?P<confidence>[^,]+),\s*"
        #                      "(?P<gpsSpeed>[^\s]+)"
        #                      ".*")
        # match = line_re.search(line)
        # if match:
        #     gps_d = match.groupdict()
        #
        #     # Add markers to the map
        #     nav_msg.gps_point = GpsPoint(gps_d["confidence"].lower().strip(),
        #                            gps_d["lat"],
        #                            gps_d["lon"],
        #                            gps_d["dist"],
        #                            gps_d["gpsSpeed"])
        # return (nav_msg)

    # def parseLine(self, line, header, i_marker_count):
    #     # gps_line_re = re.compile(".*NavMan.*\((?P<confidence>.*?),(?P<lat>[^,]+),(?P<lon>[^,]+)")
    #     n = Navigation()
    #     line_re = re.compile(".*Publishing NavigationMessage\("
    #                          "(?P<lat>[^,]+),\s*(?P<lon>[^,]+),\s*(?P<dist>\d+),\s*"
    #                          "(?P<confidence>[^,]+),\s*"
    #                          "(?P<gpsSpeed>[^\s]+)"
    #                          ".*")
    #     match = line_re.search(line)
    #     if match:
    #         gps_d = match.groupdict()
    #
    #         # Add markers to the map
    #         n.gps_point = GpsPoint(gps_d["confidence"].lower().strip(),
    #                                gps_d["lat"],
    #                                gps_d["lon"],
    #                                gps_d["dist"],
    #                                gps_d["gpsSpeed"])

    def drawNavigationMessage(self, prev, n_repeat, map):
        # Are we now in low speed (<1kph)?
        if plot_low_speed_circle(map, prev):
            return

        if plot_every_nth_confidence_marker(['high'], n_repeat):
            return


        # If was HIGH conf and still HIGH, then only map every N samples
        if (self.confidence == 'high' and n.gps_point.confidence == self.gps_previous.confidence):
            self.gps_previous = copy.deepcopy(n.gps_point)
            if not Navigation.i_repeat % 50:
                i_marker_count[0] += 1
                speed_radius = float(n.gps_point.gpsSpeed) / 5
                tool_tip = header.hours + ":" + header.minutes
                folium.CircleMarker(location=[n.gps_point.lat, n.gps_point.lon],
                                    popup=gps_d,
                                    color='green',
                                    radius=speed_radius,
                                    tooltip=tool_tip,
                                    fill=True).add_to(self.gps_map)
            Navigation.i_repeat += 1
            return

        # Will not update map for conf levels.
        Navigation.i_repeat = 0
        draw_marker = True
        if n.gps_point.confidence == 'high':
            icon_colour = 'green'
        elif n.gps_point.confidence == 'medium':
            icon_colour = 'orange'
        elif n.gps_point.confidence == 'low':
            draw_marker = False
            icon_colour = 'purple'
            low_radius = int(n.gps_point.dist) - int(self.gps_previous.dist)
            # Draw circles with increasing radius (of distance travelled)
            i_marker_count[0] += 1
            folium.Circle([self.gps_previous.lat, self.gps_previous.lon],
                          radius=low_radius,
                          fill=False,
                          color=icon_colour,
                          tooltip=str(low_radius)). \
                add_to(self.gps_map)
        else:
            # error (or other?)
            # Don't map consecutive errors
            if self.gps_previous.confidence == 'error':
                return

            draw_marker = True
            icon_colour = 'red'
            # Copy previous lat/long, but retain confidence
            confidence = n.gps_point.confidence
            n.gps_point = copy.deepcopy(self.gps_previous)
            n.gps_point.confidence = confidence
            i_marker_count[0] += 1
            folium.Circle([n.gps_point.lat, n.gps_point.lon],
                          radius=500,
                          fill=False,
                          color=icon_colour,
                          tooltip=gps_d). \
                add_to(self.gps_map)

    def plot_low_speed_circle(self, map, prev):
        plotted = False
        if (("low" != self.confidence and self.confidence != "error") and
                (float(self.dist) < 1.0 and float(self.gps_previous.dist) >= 1.0)):
            i_marker_count[0] += 1
            folium.Circle([prev.lat, prev.lon],
                          radius=200,
                          fill=False,
                          color='blue',
                          tooltip=gps_d). \
                add_to(map)
            plotted = True
        return plotted

    #
    #         if draw_marker:
    #             # print('draw_marker:', n.gps_point.lat, n.gps_point.lon)
    #             i_marker_count[0] += 1
    #             folium.Marker(location=[n.gps_point.lat, n.gps_point.lon],
    #                           popup=gps_d,
    #                           icon=folium.Icon(icon_colour)). \
    #                 add_to(self.gps_map)
    #
    #             # save current to previous
    #             self.gps_previous = copy.deepcopy(n.gps_point)
