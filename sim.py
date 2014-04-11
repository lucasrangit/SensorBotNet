#!/usr/bin/env python
#
# SensorBot Simulator
# 
import sys
import urllib2
import time
import random



def main(argv):
  server_ip = "localhost"
  server_port = "8080"

  # initialize sensors
  device = dict()
  device['id'] = 0
  device['uptime'] = 0
  device['digital1'] = 0
  device['digital1'] = 0
  device['analog1'] = 0.0

  last_device = dict() 

  while True:
    # update test sensor data 
    device['uptime'] += 1
    device['id'] = random.randint(1,10)
    device['digital1'] = random.randint(0, 1)
    device['digital2'] = random.randint(0, 1)
    device['analog1'] = random.randint(0.0, 5) # FIXME make float 

    # build status message
    status = "update"
    first = True
    for key,value in device.items():
      if first:
        status += "?"
        first = False
      else:
        status += "&"
      status += key + "=" + str(value)
    print status

    # send status message
    try:
      urllib2.urlopen("http://" + server_ip + ":" + server_port + "/" + status).read()
    except:
      pass
    time.sleep(10)

if __name__ == "__main__":
  main(sys.argv)
