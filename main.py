import datetime
import jinja2
import os
import webapp2
import urllib2

import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.ext import db
from webapp2_extras import sessions

from google.appengine.api import mail

from models import Device, Status, Subscriber
from statusbot import StatusBot

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
    subscriber = device.subscriber_set.filter('email =', email).filter('trigger_state =', "ready").get()
    if subscriber:
      self.response.out.write('<p>Already subscribed: ' + subscriber.email + '</p>')
      return

    subscriber = Subscriber(device=device, email=email)
    subscriber.trigger_state = "ready"
    subscriber.put()

    self.response.out.write('<p>Subscribed: ' + subscriber.email + '</p>')
    
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

      # determine next state
      current_state = device.state
      next_state = StatusBot().next_state(current_state).action(analog1)
      logging.info('state: %s -> %s' % (current_state, next_state))
      # update state
      if current_state != next_state:
        device.state = next_state
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
          sender='StatusBot <statusbotnet@appspotmail.com>',
          to=subscriber_email_list,
          subject='StatusBot #' + device.key().name() + ' Update!',
          body="State has changed to " + device.state)
        message.send()

    else:
      logging.info('Update new device')
      device = Device(key_name=dev_id)
      device.uptime = uptime
      device.put()

    # save device status
    status = Status(device=device)
    status.digital1 = digital1
    status.digital2 = digital2
    status.analog1 = analog1
    status.put()

    self.response.out.write('<p>OK</p>')


class DeviceHandler(webapp2.RequestHandler):

  def get(self):
    # get recent status updates and filter by device ID if specified
    try:
      device_id = int(self.request.path.split('/')[1])
      device = Device.get_by_key_name(str(device_id))
      expire_at = datetime.datetime.now() - datetime.timedelta(minutes = 30)
      if expire_at > device.updated:
        device.state = "unknown"
        device.put()
      status_list = device.status_set.order('-created').fetch(limit=10)
      subscriber_list = device.subscriber_set
      # only select those with active triggers
      subscriber_list.filter('trigger_state = ', "ready")
    except:
      logging.info('Unknown device')
      self.redirect('/')
      return

    template = template_env.get_template('device.html')
    context = {
      'device' : device,
      'status_list': status_list,
      'subscriber_list': subscriber_list,
      'datetime': datetime.datetime.now(),
    }
    self.response.out.write(template.render(context))


class MainHandler(webapp2.RequestHandler):

  def get(self):
    device_list = db.Query(Device)
    template = template_env.get_template('main.html')
    context = {
      'device_list': device_list,
    }
    self.response.out.write(template.render(context))


application = webapp2.WSGIApplication(
  [('/subscribe', SubscribePage), ('/update', UpdateHandler), 
    ('/[0-9]+', DeviceHandler), ('/.*', MainHandler)],
  config=config,
  debug=True)


