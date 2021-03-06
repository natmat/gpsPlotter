import copy
import folium

MAP_EVERY_NTH_POINT = 20


def deepcopy_nav_msg(nav_msg):
    # nav_msg.print_me()

    # print (nav_msg)
    if nav_msg.confidence not in ['low', 'error']:
        Mapping.previous_nav_msg = copy.deepcopy(nav_msg)


def is_duplicate_conf(nm):
    return (Mapping.previous_nav_msg is not None and
            Mapping.previous_nav_msg.confidence == nm.confidence)


class Mapping:
    map_count = 1
    previous_nav_msg = None  # The previously mapped NavMsg
    map_hours = None
    low_speed = False
    conf_colours = {
        'high': 'green',
        'medium': 'orange',
        'low': 'purple',
        'error': 'red',
        'lowspeed': 'blue'
    }

    def __init__(self, name):
        # Create a basemap centred somewhere around East Anglia
        self.map_name = name
        if Mapping.previous_nav_msg is None:
            self.map = folium.Map(location=[52.617, 1.3144], zoom_start=9)
        else:
            self.map = folium.Map(location=Mapping.previous_nav_msg.get_gps(), zoom_start=9)

        self.marker_count = 0
        self.i_repeat = 0

    def plot_nav_msg(self, nav_msg, header):
        if not Mapping.map_hours or Mapping.map_hours is None:
            Mapping.map_hours = header.hours

        # Are we now in low speed (<1kph)?
        try:
            if self.plot_low_speed_circle(nav_msg, header):
                return
        except ValueError as e:
            print(nav_msg.gps_speed)
            return

        # Plot Nth 'high' conf points
        self.plot_on_map(nav_msg, header)
        deepcopy_nav_msg(nav_msg)

    def plot_on_map(self, nav_msg, header):
        # Map only every Nth repeated point
        self.i_repeat += 1
        # print(self.i_repeat)

        if nav_msg.confidence == "high" and is_duplicate_conf(nav_msg):
            if not self.i_repeat % MAP_EVERY_NTH_POINT:
                # print('map Nth at ', nav_msg.get_gps())
                self.marker_count += 1
                hhmmss = '{}'.format(header.hours + ":" + header.minutes + ":" + header.seconds)
                folium.Circle(location=nav_msg.get_gps(),
                              color=self.conf_colours[nav_msg.confidence],
                              radius=float(nav_msg.gps_speed) * 5,
                              popup=hhmmss,  # nav_msg,
                              tooltip=nav_msg.dist,
                              fill=True).add_to(self.map)
                self.i_repeat = 0
            return

        # Will not update map for conf levels.
        draw_marker = True
        if nav_msg.confidence == 'high':
            icon_colour = 'green'
        elif nav_msg.confidence == 'medium':
            icon_colour = 'orange'
        elif nav_msg.confidence == 'low':
            nav_msg.set_gps(Mapping.previous_nav_msg)

            # Draw circles with increasing radius (of distance travelled)
            draw_marker = False
            icon_colour = 'purple'
            dist_travelled = int(nav_msg.dist) - int(Mapping.previous_nav_msg.dist)
            self.marker_count += 1
            folium.Circle(nav_msg.get_gps(),
                          radius=dist_travelled,
                          fill=False,
                          color=icon_colour,
                          tooltip=str(dist_travelled)). \
                add_to(self.map)
        else:
            # error (or other?)
            # Don't map consecutive ERROR
            if Mapping.previous_nav_msg is None:
                return

            if Mapping.previous_nav_msg.confidence == 'error':
                return

            # Only print valid points
            if not Mapping.previous_nav_msg.isValid():
                # print("previous lat/lon invalid")
                return

            # Draw only circle for error
            draw_marker = False
            self.marker_count += 1
            folium.Circle(Mapping.previous_nav_msg.get_gps(),
                          radius=500,
                          fill=False,
                          color=self.conf_colours['error'],
                          tooltip=nav_msg.confidence). \
                add_to(self.map)

        if draw_marker:
            if not nav_msg.isValid():
                print("ERROR")
                return

            # print('draw_marker:', nav_msg.lat, nav_msg.lon)
            self.marker_count += 1
            hhmmss = '{}'.format(header.hours + ":" + header.minutes + ":" + header.seconds)
            popup = nav_msg.lat + "," + nav_msg.lon
            folium.Marker(location=nav_msg.get_gps(),
                          popup=popup,
                          tooltip=hhmmss,
                          icon=folium.Icon(self.conf_colours[nav_msg.confidence])). \
                add_to(self.map)

            # # save current to previous
            # self.deepcopy_nav_msg(nav_msg)

    def plot_low_speed_circle(self, nav_msg, header):
        if nav_msg.confidence in ['error', 'low']:
            return

        plotted = False
        if Mapping.previous_nav_msg is None:
            return

        # If we are now low_speed, then plot Marker
        if float(nav_msg.gps_speed) < 1:
            if Mapping.low_speed:
                return plotted

            Mapping.low_speed = True
            self.marker_count += 1
            hhmmss = '{}'.format(header.hours + ":" + header.minutes + ":" + header.seconds)
            folium.Marker(nav_msg.get_gps(),
                          color=self.conf_colours['lowspeed'],
                          tooltip=hhmmss).\
                      add_to(self.map)
            plotted = True
            self.i_repeat = -1
        else:
            Mapping.low_speed = False

        return plotted

    def draw_map(self, log_hours):
        if Mapping.map_hours is None:
            return

        if log_hours > Mapping.map_hours:
            self.save_map_file()
            self.marker_count = 0
            Mapping.map_hours = log_hours
            return True
        return False

    def save_map_file(self):
        if Mapping.map_hours is None:
            Mapping.map_hours = 99
        map_file = "{}.{:0>2d}hr.map.html".format(self.map_name, int(Mapping.map_hours))
        print("Writing {} markers to file {}".format(self.marker_count, map_file))

        # Re-centre map before saving
        try:
            self.map.location = Mapping.previous_nav_msg.get_gps()
            self.map.save(map_file)
            Mapping.map_count += 1
            del self.map
        except ValueError as e:
            print(e)
            return

