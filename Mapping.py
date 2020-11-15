import copy
import folium

MAP_EVERY_NTH_POINT = 5


class Mapping:
    map_count = 1
    previous_nav_msg = None # The previously mapped NavMsg
    map_hours = None

    def __init__(self, name):
        # Create a basemap centred somewhere around East Anglia
        self.map_name = name;
        self.map = folium.Map(location=[52.617, 1.3144], zoom_start=9)
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
        if self.plot_every_nth_confidence_marker(['high'], nav_msg, header):
            return

        self.deepcopy_nav_msg(nav_msg)

    def deepcopy_nav_msg(self, nav_msg):
        # nav_msg.print_me()

        # print (nav_msg)
        if nav_msg.confidence != 'error':
            Mapping.previous_nav_msg = copy.deepcopy(nav_msg)

    def plot_every_nth_confidence_marker(self, confidence_set, nav_msg, header):
        print ("i={}".format(self.i_repeat))
        # Map only every Nth repeated point
        if (nav_msg.confidence in confidence_set and nav_msg.confidence == Mapping.previous_nav_msg.confidence):
            if not self.i_repeat % MAP_EVERY_NTH_POINT:
                self.marker_count += 1
                speed_radius = float(nav_msg.gps_speed) / 5
                hours_mins = header.hours + ":" + header.minutes
                folium.CircleMarker(location=nav_msg.get_gps(),
                                    popup=hours_mins,  # nav_msg,
                                    color='green',
                                    radius=nav_msg.gps_speed,
                                    tooltip=hours_mins + ":" + nav_msg.gps_speed,
                                    fill=True).add_to(self.map)
            self.i_repeat += 1
            return

        # Will not update map for conf levels.
        self.i_repeat = 0
        draw_marker = True
        if nav_msg.confidence == 'high':
            icon_colour = 'green'
        elif nav_msg.confidence == 'medium':
            icon_colour = 'orange'
        elif nav_msg.confidence == 'low':
            draw_marker = False
            icon_colour = 'purple'
            low_radius = int(nav_msg.dist) - int(Mapping.previous_nav_msg.dist)
            # Draw circles with increasing radius (of distance travelled)
            self.marker_count += 1
            folium.Circle(Mapping.previous_nav_msg.get_gps(),
                          radius=low_radius,
                          fill=False,
                          color=icon_colour,
                          tooltip=str(low_radius)). \
                add_to(self.map)
        else:
            # error (or other?)
            # Don't map consecutive errors
            if Mapping.previous_nav_msg.confidence == 'error':
                return

            draw_marker = True
            icon_colour = 'red'
            # Copy previous lat/long, but retain confidence
            confidence = nav_msg.confidence
            nav_msg = copy.deepcopy(Mapping.previous_nav_msg)
            nav_msg.confidence = confidence

            self.marker_count += 1
            folium.Circle(nav_msg.get_gps(),
                          radius=500,
                          fill=False,
                          color=icon_colour,
                          tooltip=nav_msg.confidence). \
                add_to(self.map)

        if draw_marker:
            # print('draw_marker:', nav_msg.lat, nav_msg.lon)
            self.marker_count += 1
            hours_mins = '{}'.format(header.hours + ":" + header.minutes)  # nav_msg)
            folium.Marker(location=nav_msg.get_gps(),
                          popup=hours_mins,
                          icon=folium.Icon(icon_colour)). \
                add_to(self.map)

            # save current to previous
            self.deepcopy_nav_msg(nav_msg)

    def plot_low_speed_circle(self, nav_msg):
        plotted = False
        if not Mapping.previous_nav_msg:
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
        input("Press Enter to continue...")

        # Create new map
        del self.map
        self.map = folium.Map(location=Mapping.previous_nav_msg.get_gps(), zoom_start=9)
