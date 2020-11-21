import re
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
        return "[{},{}]:{},{},{}".format(self.lat, self.lon, self.confidence, self.gps_speed, self.dist)

    def get_gps(self):
        return [self.lat, self.lon]

    def set_gps(self, gps_copy):
        self.lat = gps_copy.lat
        self.lon = gps_copy.lon

    def set_gps_point(self, gps_map, gps_point, gps_previous):
        self.gps_map = gps_map
        self.gps_point = gps_point
        self.gps_previous = gps_previous

    def isValid(self):
        return (self.lat != '0' and self.lon != '0')

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
