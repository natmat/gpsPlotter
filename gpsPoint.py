class GpsPoint:
  def __init__(self, confidence, lat, lon, dist, gpsSpeed):
    self.confidence = [] if confidence is None else confidence
    self.lat = [] if lat is None else lat
    self.lon = [] if lon is None else lon
    self.dist = [] if dist is None else dist
    self.gpsSpeed = [] if gpsSpeed is None else gpsSpeed

