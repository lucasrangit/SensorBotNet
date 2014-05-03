# StatusBot.net Google App Engine web app. Main handler that serves up the website.
#
# Copyright (C) 2014  Lucas Rangit MAGASWERAN <lucas.magasweran@ieee.org>
# This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE.
# This is free software, and you are welcome to redistribute it under certain
# conditions; see LICENSE for details.
#
import datetime
import jinja2
import os
import webapp2
import urllib2
from email.utils import parseaddr

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
    if parseaddr(email) == ('', ''):
      self.response.out.write('<p>Invalid email</p>')
      return

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
    except ValueError:
      logging.info('Input error')
      self.response.out.write('<p>Input error</p>')
      return 

    device = Device.get_by_key_name(dev_id)
    if device:
#      logging.info('Update existing device')
      device.uptime = uptime

      # determine next state
      # TODO make one line
      current_state = device.status_set.order('-created').get().state
      if current_state:
        next_state = StatusBot().next_state(current_state).action(True if analog1 > 4.9 else False)
      else:
        current_state = 'unknown'

      # update state
      # this is why device status is saved on state change only
      if current_state != next_state:
        logging.info('state: %s -> %s' % (current_state, next_state))
        status = Status(device=device)
        status.state = next_state
        status.digital1 = digital1
        status.digital2 = digital2
        status.analog1 = analog1
        status.put()

      # send notification to subscribers who's trigger state is the current state
      subscriber_list = device.subscriber_set.filter('trigger_state =', current_state)
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
          sender='StatusBot.net <donotreply@statusbotnet.appspotmail.com>',
          to=subscriber_email_list,
          subject='StatusBot #' + device.key().name() + ' Update!',
          body="State has changed to " + current_state)
        message.send()

    else:
      logging.info('Update new device')
      device = Device(key_name=dev_id)
      device.uptime = uptime
      device.put()
      # save device status when a device is added for the first time
      status = Status(device=device)
      status.digital1 = digital1
      status.digital2 = digital2
      status.analog1 = analog1
      status.put()

    self.response.out.write('<p>OK</p>')


class DeviceHandler(webapp2.RequestHandler):

  def get(self):
    # get recent status updates and filter by device ID if specified
    device_id = int(self.request.path.split('/')[1])
    device = Device.get_by_key_name(str(device_id))
    if not device:
      logging.info('Unknown device')
      self.redirect('/')
      return

    # expire status updates that are 30 minutes old
    expire_at = datetime.datetime.now() - datetime.timedelta(minutes = 30)
    status_list = device.status_set.order('-created').fetch(limit=10)
    current_state = status_list[0].state
    if current_state:
      # device has status history
      if expire_at > device.updated:
        current_state = 'unknown'
    else:
      # device status is unknown (has this device not come online yet?)
      current_state = 'unknown'

    status_last_ready = device.status_set.filter('state =', 'ready').get()
    subscriber_list = device.subscriber_set
    # only select those with active triggers
    subscriber_list.filter('trigger_state = ', 'ready')

    template = template_env.get_template('device.html')
    context = {
      'device' : device,
      'current_state': current_state,
      'status_list': status_list,
      'status_last_ready': status_last_ready,
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


