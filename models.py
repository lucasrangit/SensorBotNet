from google.appengine.ext import db

# Device ID is stored as the key_name
class Device(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True)
  uptime = db.IntegerProperty()
  state = db.StringProperty()

class Status(db.Model):
  device = db.ReferenceProperty(Device,required=True) 
  created = db.DateTimeProperty(auto_now_add=True)
  digital1 = db.IntegerProperty()
  digital2 = db.IntegerProperty()
  analog1 = db.FloatProperty()

class Subscriber(db.Model):
  device = db.ReferenceProperty(Device,required=True)
  email = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  trigger_state = db.StringProperty()
    
