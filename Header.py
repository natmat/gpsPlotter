class Header:
  def __init__(self, d):
    self.date = [] if d is None else d["date"]
    self.hours = [] if d is None else d["hours"]
    self.minutes = [] if d is None else d["minutes"]
    self.seconds = [] if d is None else d["seconds"]
    self.ip_addr = [] if d is None else d["ip_addr"]
    self.service = [] if d is None else d["service"]

    # self.date = [] if date is None else date
    # self.hours = [] if hours is None else hours
    # self.minutes = [] if minutes is None else minutes
    # self.seconds = [] if seconds is None else seconds
    # self.ip_addr = [] if ip_addr is None else ip_addr
    # self.service = [] if service is None else service

