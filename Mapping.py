import copy
import folium

MAP_EVERY_NTH_POINT = 20


class Mapping:
    map_count = 1

    def __init__(self, name):
        # Create a basemap centred somewhere around East Anglia
        self.map_name = name;
        self.map = folium.Map(location=[52.617, 1.3144], zoom_start=10)
        self.marker_count = 0
        self.i_repeat = 0

    def plot_nav_msg(self, nav_msg_prev, nav_msg, header):
        if nav_msg_prev is None:
            return

        # Are we now in low speed (<1kph)?
        if self.plot_low_speed_circle(nav_msg, nav_msg_prev):
            return

        # Plot Nth 'high' conf points
        if self.plot_every_nth_confidence_marker(['high'], nav_msg, nav_msg_prev, header):
            return

    def plot_every_nth_confidence_marker(self, confidence_set, nav_msg, nav_msg_prev, header):
        # Map only every Nth repeated point
        if (nav_msg.confidence in confidence_set and nav_msg.confidence == nav_msg_prev.confidence):
            if not self.i_repeat % MAP_EVERY_NTH_POINT:
                self.marker_count += 1
                speed_radius = float(nav_msg.gps_speed) / 5
                tool_tip = header.hours + ":" + header.minutes + "_" + nav_msg.gps_speed
                folium.CircleMarker(location=[nav_msg.lat, nav_msg.lon],
                                    popup="PopUp",  # nav_msg,
                                    color='green',
                                    radius=speed_radius,
                                    tooltip=tool_tip,
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
            low_radius = int(nav_msg.dist) - int(nav_msg_prev.dist)
            # Draw circles with increasing radius (of distance travelled)
            self.marker_count += 1
            folium.Circle([self.gps_previous.lat, self.gps_previous.lon],
                          radius=low_radius,
                          fill=False,
                          color=icon_colour,
                          tooltip=str(low_radius)). \
                add_to(self.map)
        else:
            # error (or other?)
            # Don't map consecutive errors
            if nav_msg_prev.confidence == 'error':
                return

            draw_marker = True
            icon_colour = 'red'
            # Copy previous lat/long, but retain confidence
            confidence = nav_msg.confidence
            nav_msg = copy.deepcopy(nav_msg_prev)
            nav_msg.confidence = confidence
            self.marker_count += 1
            folium.Circle([nav_msg.lat, nav_msg.lon],
                          radius=500,
                          fill=False,
                          color=icon_colour,
                          tooltip=nav_msg.confidence). \
                add_to(self.map)

        if draw_marker:
            # print('draw_marker:', nav_msg.lat, nav_msg.lon)
            self.marker_count += 1
            popup = '{}'.format("PopUp")  # nav_msg)
            folium.Marker(location=[nav_msg.lat, nav_msg.lon],
                          popup=popup,
                          icon=folium.Icon(icon_colour)). \
                add_to(self.map)

            # save current to previous
            self.gps_previous = copy.deepcopy(nav_msg)

    def plot_low_speed_circle(self, message, prev):
        plotted = False
        if (float(prev.dist) >= 1.0) and (float(message.dist) < 1.0):
            if (message.confidence not in ['error', 'low']):
                self.marker_count += 1
                folium.Circle([prev.lat, prev.lon],
                              radius=200,
                              fill=False,
                              color='blue',
                              tooltip=message.gps_speed). \
                    add_to(self.map)
                plotted = True
        return plotted

    def draw_map(self):
        if self.marker_count > 500:
            self.marker_count = 0
            self.save_map_file()
            return True
        return False

    def save_map_file(self):
        print("save_map_file")
        map_file = self.map_name + "." + str(Mapping.map_count) + ".map.html"
        Mapping.map_count += 1
        print("Writing to file {}".format(map_file))
        self.map.save(map_file)
        self.map = folium.Map(location=[52.617, 1.3144], zoom_start=10)
