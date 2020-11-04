
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

  def get_hours(self):
    return(self.hours)

def main():
  test_line = " 2020/10/29 10:05:00.038423342 10.177.156.21 AUD Navigation Navigation.cpp@325: Publishing NavigationMessage( 0, 0, 0, ERROR, 0 )"
  h = Header()
  h.stripHeader(test_line)

  #Use list comprehension to remove the header from line
  line_header = ' '.join([str(elem) for elem in test_line.split()[:5]])
  line_without_header = ' '.join([str(elem) for elem in test_line.split()[5:]])
  print(line_header)
  print(line_without_header)
  
  return(line_without_header)

if __name__ == "__main__":
  # execute only if run as a script
  main()

