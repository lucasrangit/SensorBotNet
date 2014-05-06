# StatusBot.net Google App Engine web app. Data model.
#
# Copyright (C) 2014  Lucas Rangit MAGASWERAN <lucas.magasweran@ieee.org>
# This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE.
# This is free software, and you are welcome to redistribute it under certain
# conditions; see LICENSE for details.
#
from google.appengine.ext import db

# Device ID is stored as the key_name
class Device(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True,indexed=False)
  uptime = db.IntegerProperty(indexed=False)
  model_name = db.StringProperty(required=True,default='generic',indexed=False)
  location = db.StringProperty(required=True,default='unknown', indexed=False)
  state = db.StringProperty(required=True,default='unknown')
  ready = db.DateTimeProperty()

#class Status(db.Model):
#  created = db.DateTimeProperty(auto_now_add=True)
#  device = db.ReferenceProperty(Device,required=True)
#  state = db.StringProperty(default='unknown')
#  digital1 = db.IntegerProperty(indexed=False)
#  digital2 = db.IntegerProperty(indexed=False)
#  analog1 = db.FloatProperty(indexed=False)

class Subscriber(db.Model):
  device = db.ReferenceProperty(Device,required=True)
  email = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True,indexed=False)
  trigger_state = db.StringProperty()

