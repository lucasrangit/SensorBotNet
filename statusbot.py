# StatusBot.net Google App Engine web app. Generic StatusBot state machine.
#
# Copyright (C) 2014  Lucas Rangit MAGASWERAN <lucas.magasweran@ieee.org>
# This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE.
# This is free software, and you are welcome to redistribute it under certain
# conditions; see LICENSE for details.
#
class State(object):

#  def __init__(self, start):
#    self.new_state(start)

#  def new_state(self, state):
#    self.__class__ = state

  def action(self, data):
    raise NotImplementedError()

class Unknown(State):

  def action(self, data):
    return 'idle'

class Idle(State):

  def action(self, data):
    if data:
      return 'not_ready_1'

    return 'idle'

class NotReady_1(State):

  def action(self, data):
    if data:
      return 'not_ready_2'

    return 'idle'

class NotReady_2(State):

  def action(self, data):
    if data:
      return 'not_ready'
    
    return 'idle'

class NotReady(State):

  def action(self, data):
    if not data:
      return 'ready_1'
    
    return 'not_ready'

class Ready_1(State):

  def action(self, data):
    if not data:
      return 'ready_2'

    return 'idle'

class Ready_2(State):

  def action(self, data):
    if not data:
      return 'ready'

    return 'idle'

class Ready(State):

  def action(self, data):
    return 'idle' 

class StatusBot(object):

  states = {
    'unknown': Unknown(),
    'idle': Idle(),
    'not_ready_1': NotReady_1(),
    'not_ready_2': NotReady_2(),
    'not_ready': NotReady(),
    'ready_1': Ready_1(),
    'ready_2': Ready_2(),
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


