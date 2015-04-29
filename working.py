#!/usr/bin/env python

import serial
import io
import time
import sys
from termcolor import colored

## BEGIN RRDTOOL
import rrdtool
## END RRDTOOL

degc = "c"
degf = "f"

setting = 20.0
loth = 0.5
hith = 0.5

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Printer():
  """
  Print things to stdout on one line dynamically
  """
  
  def __init__(self,data):
  
    sys.stdout.write("\r\x1b[K"+data.__str__())
    sys.stdout.flush()

stateoff = colored("off", "green")
stateon = colored("on", "red")

tstate = stateoff

def open_port( portid = 0 ):
  ser = serial.Serial(0)
  ser.baudrate = 2400
  ser.bytesize = 8
  ser.parity = 'N'
  ser.stopbits = 2
  ser.timeout = 1
  
  if not ser.isOpen():
    ser.open()
  
  if ser.isOpen():
    return [ser, ser.readline()]
  else:
    return [None, "Error opening serial port"]
  
def close_port( s ):
  if s.isOpen():
    s.close()

# Get serial port handle
ser, result = open_port(0)

if ser is None:
  print result
  sys.exit(1)
else:
  print "Detected temperature sensor board, details: %s" % (result.strip())
  boardid = result.strip().split(" ")
  print "using units %s" % (boardid[-1])
  if boardid[-1] == "C":
    units = degc
  else:
    units = degf

print "Press [Ctrl]-[C] to exit..."

valarr = [0,0,0,0]
lastupdate = time.gmtime()

try:
  while True:
    line = str(ser.readline()).split(" ")
    valarr[int(line[0])-1] = float(line[1].strip())
    if int(line[0]) == 4:
      ## BEGIN RRDTOOL
      ret = rrdtool.update('db/temp.rrd', 'N:%s:%s' %(valarr[0], valarr[3]));
      ## END RRDTOOL
      tavg = ((valarr[0] + valarr[3]) / 2)
      if time.mktime(time.gmtime()) - time.mktime(lastupdate) >= 600:
        if tavg > (setting + hith):
          newstate = stateoff
        if tavg < (setting + loth):
          newstate = stateon
        if newstate != tstate:
          tstate = newstate
          lastupdate = time.gmtime()
      output = "%s\t[1] %2.2f%1s\t[4] %2.2f%1s\t[A] %2.2f%1s\tHeating: %s" % (time.strftime("%c", lastupdate), valarr[0], units, valarr[3], units, tavg, units, tstate)
      Printer(output)  
#    time.sleep(1)
except KeyboardInterrupt:
  pass

print "\n\nClosing serial port, thank you!"
close_port(ser)

