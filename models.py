from google.appengine.ext import db

# Device ID is stored as the key_name
class Device(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True,indexed=False)
  uptime = db.IntegerProperty(indexed=False)
  state = db.StringProperty(default='Unknown')
  kind = db.StringProperty(required=True,default='Unknown',indexed=False)

class Status(db.Model):
  device = db.ReferenceProperty(Device,required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  digital1 = db.IntegerProperty(indexed=False)
  digital2 = db.IntegerProperty(indexed=False)
  analog1 = db.FloatProperty(indexed=False)

class Subscriber(db.Model):
  device = db.ReferenceProperty(Device,required=True)
  email = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True,indexed=False)
  trigger_state = db.StringProperty()

