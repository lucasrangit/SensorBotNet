class State(object):

#  def __init__(self, start):
#    self.new_state(start)

#  def new_state(self, state):
#    self.__class__ = state

  def action(self, data):
    raise NotImplementedError()

class Unknown(State):

  def action(self, data):
    if data > 4.9:
      return 'idle'
    
    return 'unknown' 

class Idle(State):

  def action(self, data):
    if data <= 4.9:
      return 'not_ready'
    
    return 'idle'

class NotReady(State):

  def action(self, data):
    if data > 4.9:
      return 'ready'
    
    return 'not_ready'

class Ready(State):

  def action(self, data):
    return 'idle' 

class StatusBot(object):

  states = {
    'unknown': Unknown(),
    'idle': Idle(),
    'not_ready': NotReady(),
    'ready': Ready(),
  }

#  def __init__(self, start_state):
#    self.start_state = start_state

  def next_state(self, state_name):
    state = StatusBot.states.get(state_name)
    if state is None:
      print "Unrecognized state: %s" % state_name
      state = Unknown()  
    return state

#  def opening_state(self):
#    return self.next_state(self.start_state)


