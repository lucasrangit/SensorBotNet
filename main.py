import datetime
import jinja2
from models import Device, Status, Subscriber
import os
import webapp2
import urllib2

import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.ext import db
from webapp2_extras import sessions

from google.appengine.api import mail

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='')

template_env = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'templates')))

class SubscribePage(webapp2.RequestHandler):

  def post(self):
    device_id = self.request.get('device_id')
    device = Device.get_by_key_name(device_id)
    if not device:  
      self.response.out.write('<p>Device does not exist</p>')
      return
      
    email = self.request.get('email')
    subscriber = Subscriber(device=device, email=email)
    subscriber.trigger_state = "Ready"
    subscriber.put()

    self.response.out.write('<p>Subscribed</p>')
    
class UpdateHandler(webapp2.RequestHandler):

  def get(self):

    try:
      dev_id = self.request.get('id')
      uptime = int(self.request.get('uptime'))
      digital1 = int(self.request.get('digital1'))
      digital2 = int(self.request.get('digital2'))
      analog1 = float(self.request.get('analog1'))

    except: 
      logging.info('Input error')
      self.response.out.write('<p>Input error</p>')
      return 

    device = Device.get_by_key_name(dev_id)
    if device:
#      logging.info('Update existing device')
      device.uptime = uptime

      # update state
      current_state = device.state
      if current_state == "Unknown" or current_state == "Available":
        if analog1 < 5.0:
          device.state = "Busy"

      elif current_state == "Busy":
        if analog1 >= 5.0:
          device.state = "Ready"

      elif current_state == "Ready":
        device.state = "Available"

      device.put()

      # send notification to subscribers who's trigger state is the current state
      subscriber_list = device.subscriber_set.filter('trigger_state =', device.state)
      subscriber_email_list = list()
      for subscriber in subscriber_list:
        subscriber_email_list.append(subscriber.email)
        # instead of deleting the subscriber, clear the trigger state
        # so that a record of the subscriber is kept but no further email
        # is sent
        subscriber.trigger_state = "" 
        subscriber.put()

      if len(subscriber_email_list) > 0:
        message = mail.EmailMessage(
          sender='StatusBot <StatusBot@appspotmail.com>',
          to=subscriber_email_list,
          subject='StatusBot #' + device.key().name() + ' Update!',
          body="State has changed to " + device.state)
        message.send()

    else:
      logging.info('Update new device')
      device = Device(key_name=dev_id, state="Unknown")
      device.uptime = uptime
      device.put()

    # save device status
    status = Status(device=device)
    status.digital1 = digital1
    status.digital2 = digital2
    status.analog1 = analog1
    status.put()
    
class MainHandler(webapp2.RequestHandler):

  def get(self):
    # get recent status updates and filter by device ID if specified
    try:
      device_id = int(self.request.path.split('/')[1])
      device = Device.get_by_key_name(str(device_id))
      status_list = device.status_set.order("-created").fetch(limit=10)
      subscriber_list = device.subscriber_set
    except:
      device = None
      status_list = db.Query(Status).order("-created").fetch(limit=10)
      subscriber_list = []

    template = template_env.get_template('home.html')
    context = {
      'device' : device,
      'status_list': status_list,
      'subscriber_list': subscriber_list,
      'datetime': datetime.datetime.now(),
    }
    self.response.out.write(template.render(context))

application = webapp2.WSGIApplication(
  [('/subscribe', SubscribePage), ('/update', UpdateHandler), ('/.*', MainHandler)],
  config=config,
  debug=True)


