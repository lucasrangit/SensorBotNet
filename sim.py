#!/usr/bin/env python
#
# StatusBot Simulator
# 
import sys
import urllib2
import time
import random

class Device(object):

  def __init__(self, num):
    self.status = dict()
    self.status['id'] = num
    self.status['uptime'] = 0

    # start all sensors either high or low
    self.status['digital1'] = random.randint(0,1)
    self.status['digital2'] = random.randint(0,1)
    self.status['analog1'] = float(random.randint(0,1)) * 5.0

    self.duty_cycle = random.randint(0,100)

  def get_status(self):
    # update and return test sensor data
    self.status['uptime'] += 1
    self.duty_cycle -= 1
    if self.duty_cycle < 0:
      # toggle 0/1 and update with a new duty cycle
      x = self.status['digital1']
      self.status['digital1'] = (x + 1) % 2
      # update with new duty cycle
      self.duty_cycle = random.randint(0,100)
    self.status['digital2'] = random.randint(0,1)
    analog1 = float(random.randint(-1,1)) * float(random.randint(0,10)) / 10.0
    self.status['analog1'] += analog1
    if self.status['analog1'] > 5.1:
      self.status['analog1'] = 5.1
    elif self.status['analog1'] < 0.0:
      self.status['analog1'] = 0.0

    return self.status

def main(argv):
  if len(sys.argv) == 1:
    print 'Usage: %s server port [device count]' % sys.argv[0]
    return

  server_ip = str(sys.argv[1])
  server_port = str(sys.argv[2])
  if len(sys.argv) > 3:
    device_count = int(sys.argv[3])
  else:
    device_count = 1

  # initialize devices
  devices = list()
  for device_num in range(0,device_count):
    devices.append(Device(device_num+1))

  while True:

    dev = devices[random.randint(0,device_count-1)]
    device = dev.get_status()
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
    time.sleep(1)

if __name__ == "__main__":
  main(sys.argv)
