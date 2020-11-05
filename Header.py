
class Header():
  def __init__(self):
    self.header = None

  def stripHeader(self, line):
    split_line = line.split()
    self.date = split_line[0]
    self.hours = split_line[1].split(":")[0]
    self.minutes = split_line[1].split(":")[1]
    self.ip_addr = split_line[2]
    self.adeiv = split_line[3]
    self.service = split_line[4]

    # Use list comprehension to remove the header from line
    line_without_header = ' '.join([str(elem) for elem in line.split()[5:]])
    return(line_without_header)

  def get_hours(self):
    return(self.hours)

def main():
  test_line = " 2020/10/29 10:05:00.038423342 10.177.156.21 AUD Navigation Navigation.cpp@325: Publishing NavigationMessage( 0, 0, 0, ERROR, 0 )"
  h = Header()
  line_without_header = h.stripHeader(test_line)
  print(line_without_header)

if __name__ == "__main__":
  # execute only if run as a script
  main()

