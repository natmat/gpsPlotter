import copy
import folium
import sys


MAP_EVERY_NTH_POINT = 5


class Mapping:
    map_count = 1
    previous_nav_msg = None # The previously mapped NavMsg
    map_hours = None

    def __init__(self, name):
        # Create a basemap centred somewhere around East Anglia
        self.map_name = name;
        if Mapping.previous_nav_msg is None:
            self.map = folium.Map(location=[52.617, 1.3144], zoom_start=9)
        else:
            self.map = folium.Map(location=Mapping.previous_nav_msg.get_gps(), zoom_start=9)

        self.marker_count = 0
        self.i_repeat = 0

    def plot_nav_msg(self, nav_msg, header):
        # print(nav_msg.get_gps())

        if not Mapping.map_hours:
            Mapping.map_hours = header.hours

        # Are we now in low speed (<1kph)?
        if self.plot_low_speed_circle(nav_msg):
            return

        # Plot Nth 'high' conf points
        self.plot_on_map(['high'], nav_msg, header)
        self.deepcopy_nav_msg(nav_msg)

    def deepcopy_nav_msg(self, nav_msg):
        # nav_msg.print_me()

        # print (nav_msg)
        if nav_msg.confidence != 'error':
            Mapping.previous_nav_msg = copy.deepcopy(nav_msg)

    def is_duplicate(self, cs, nm):
        return (nm.confidence in cs and
                Mapping.previous_nav_msg is not None and
                nm.confidence == Mapping.previous_nav_msg.confidence)

    def plot_on_map(self, confidence_set, nav_msg, header):
        # Map only every Nth repeated point
        self.i_repeat += 1
        print (self.i_repeat)
        if self.is_duplicate(confidence_set, nav_msg):
            if not self.i_repeat % MAP_EVERY_NTH_POINT:
                print ('map Nth at ', nav_msg.get_gps())
                self.marker_count += 1
                speed_radius = float(nav_msg.gps_speed) / 5
                hours_mins = '{}'.format(header.hours + ":" + header.minutes)
                folium.CircleMarker(location=nav_msg.get_gps(),
                                    popup=hours_mins,  # nav_msg,
                                    color='green',
                                    radius=100, #nav_msg.gps_speed,
                                    tooltip=hours_mins,
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
            if not nav_msg.isValid():
                print("ERR: low invalid")
                nav_msg.set_gps(Mapping.previous_nav_msg)

            # Draw circles with increasing radius (of distance travelled)
            draw_marker = False
            icon_colour = 'purple'
            low_radius = int(nav_msg.dist) - int(Mapping.previous_nav_msg.dist)
            self.marker_count += 1
            folium.Circle(nav_msg.get_gps(),
                          radius=low_radius,
                          fill=False,
                          color=icon_colour,
                          tooltip=str(low_radius)). \
                add_to(self.map)
        else:
            # error (or other?)
            # Don't map consecutive ERRORs
            if Mapping.previous_nav_msg.confidence == 'error':
                return

            # Only print valid points
            if not Mapping.previous_nav_msg.isValid():
                # print("previous lat/lon invalid")
                return

            # Draw only cirle for error
            draw_marker = False
            icon_colour = 'red'
            self.marker_count += 1
            folium.Circle(Mapping.previous_nav_msg.get_gps(),
                          radius=100,
                          fill=False,
                          color=icon_colour,
                          tooltip=nav_msg.confidence). \
                add_to(self.map)

        if draw_marker:
            if not nav_msg.isValid():
                print("ERROR")
                return

            # print('draw_marker:', nav_msg.lat, nav_msg.lon)
            self.marker_count += 1
            hours_mins = '{}'.format(header.hours + ":" + header.minutes)
            popup = nav_msg.lat + "," + nav_msg.lon
            folium.Marker(location=nav_msg.get_gps(),
                          popup=popup,
                          icon=folium.Icon(icon_colour)). \
                add_to(self.map)

            # # save current to previous
            # self.deepcopy_nav_msg(nav_msg)

    def plot_low_speed_circle(self, nav_msg):
        plotted = False
        if Mapping.previous_nav_msg is None:
            return

        if (float(Mapping.previous_nav_msg.dist) >= 1.0) and (float(nav_msg.dist) < 1.0):
            if (nav_msg.confidence not in ['error', 'low']):
                self.marker_count += 1
                folium.Circle(nav_msg.get_gps(),
                              radius=200,
                              fill=False,
                              color='blue',
                              tooltip="speed:" + nav_msg.gps_speed). \
                    add_to(self.map)
                plotted = True
        return plotted

    def draw_map(self, log_hours):
        # print('draw_map ' + log_hours + ',' + Mapping.map_hours)
        if log_hours > Mapping.map_hours:
            self.marker_count = 0
            self.save_map_file()
            Mapping.map_hours = log_hours
            return True
        return False

    def save_map_file(self):
        map_file = "{}.{:0>2d}hr.map.html".format(self.map_name, int(Mapping.map_hours))
        print("Writing to file {}".format(map_file))

        # Re-centre map before saving
        self.map.location = Mapping.previous_nav_msg.get_gps()
        self.map.save(map_file)
        Mapping.map_count += 1
        # input("Press Enter to continue...")
        del self.map
        # sys.exit(1)
