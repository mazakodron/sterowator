#!/usr/bin/python
#-*-coding: UTF-8 -*-

import sys, signal
import threading, time
try:
  import queue
except ImportError:
  import Queue as queue

from PyQt4.QtCore import QTimer, QObject, QUrl
from PyQt4.QtGui import QApplication
from PyQt4.QtDeclarative import QDeclarativeView

TURN_LEFT = 0
TURN_RIGHT = 1
GO_FORWARD = 2
GO_BACKWARD = 3
LIFT_MAZAK = 4
DROP_MAZAK = 5
END = 6

q = queue.Queue()

def sigint_handler(*args):
  global terminate
  QApplication.quit()
  raise KeyboardInterrupt

signal.signal(signal.SIGINT, sigint_handler)

class Interface(threading.Thread):

  rootObject = None
  
  def __init__(self):
    threading.Thread.__init__(self)

  def process(self):
    while not q.empty():
      action = q.get()
      if action == DROP_MAZAK:
        self.rootObject.dropMazak()
      elif action == LIFT_MAZAK:
        self.rootObject.liftMazak()
      elif action == TURN_LEFT:
        self.rootObject.rotateLeft()
      elif action == TURN_RIGHT:
        self.rootObject.rotateRight()
      elif action == GO_FORWARD:
        self.rootObject.goForward()
      elif action == GO_BACKWARD:
        self.rootObject.goBackward()
      elif action == END:
        self.rootObject.hideRobot()

  def run(self):
    app = QApplication(sys.argv)

    # Create the QML user interface.
    view = QDeclarativeView()
    
    view.setResizeMode(QDeclarativeView.SizeRootObjectToView)

    view.setSource(QUrl('symulator/mazakodron.qml'))
    rootObject = view.rootObject()
    if not rootObject:
      view.setSource(QUrl('mazakodron.qml'))
      rootObject = view.rootObject()
      
    self.rootObject = rootObject

    view.setGeometry(0, 0, 800, 600)
    view.show()

    timer = QTimer()
    timer.start(1000/60) # 60FPS
    timer.timeout.connect(self.process)

    sys.exit(app.exec_());

def open():
  global thread
  thread = Interface()
  thread.start()

def wait():
  global thread
  thread.join()

def test():
  time.sleep(1)
  q.put(DROP_MAZAK)
  time.sleep(0.2)
  q.put(LIFT_MAZAK)
  time.sleep(0.2)
  for i in range(425*8):
    q.put(TURN_LEFT)
    time.sleep(0.001)
  q.put(DROP_MAZAK)
  time.sleep(0.2)
  for i in range(500):
    time.sleep(0.01)
    q.put(GO_FORWARD)
  q.put(LIFT_MAZAK)
  time.sleep(0.2)
  for i in range(425*8):
    q.put(TURN_RIGHT)
    time.sleep(0.001)
  q.put(DROP_MAZAK)
  time.sleep(0.2)
  for i in range(200):
    time.sleep(0.01)
    q.put(GO_FORWARD)
  q.put(LIFT_MAZAK)
  time.sleep(0.2)
  for i in range(425*8):
    q.put(TURN_RIGHT)
    time.sleep(0.001)
  for i in range(600):
    time.sleep(0.01)
    q.put(GO_BACKWARD)
  for i in range(425*8):
    q.put(TURN_RIGHT)
    time.sleep(0.001)
  q.put(DROP_MAZAK)
  time.sleep(0.2)
  for i in range(500):
    time.sleep(0.01)
    q.put(GO_BACKWARD)
  q.put(LIFT_MAZAK)
  time.sleep(0.2)
  for i in range(425*2*8):
    q.put(TURN_LEFT)
    time.sleep(0.001)
  for i in range(100):
    time.sleep(0.01)
    q.put(GO_FORWARD)
  q.put(DROP_MAZAK)
  time.sleep(0.2)
  for i in range(500):
    time.sleep(0.01)
    q.put(GO_FORWARD)
  q.put(LIFT_MAZAK)
  time.sleep(0.2)
  q.put(DROP_MAZAK)
  time.sleep(0.2)
  q.put(LIFT_MAZAK)
  time.sleep(0.2)

def close():
  QApplication.quit()

pins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
steppers = [0, 0]

def doSteps():
  if steppers[0] == 0 or steppers[1] == 0:
    return
  if steppers[0] != steppers[1]:
    if steppers[0] == 1:
      q.put(GO_FORWARD)
    else:
      q.put(GO_BACKWARD)
  else:
    if steppers[0] == 1:
      q.put(TURN_LEFT)
    else:
      q.put(TURN_RIGHT)
  steppers[0] = 0
  steppers[1] = 0

def getDirection(id, val, pins):
  prev = lambda pin: 3 if pin==0 else pin-1
  next = lambda pin: 0 if pin==3 else pin+1

  if val==1 and pins[prev(id)] == 1:
    return -1
  elif val==0 and pins[next(id)] == 1:
    return -1
  elif val==1 and pins[next(id)] == 1:
    return 1
  elif val==0 and pins[prev(id)] == 1:
    return 1
  return 0

def clearPin(id):
  if pins[id]==0:
    return
  if id < 5:
    steppers[0] = getDirection(id-1, 0, [pins[1], pins[2], pins[3], pins[4]])
  elif id < 10:
    pin = id-6
    if pin<0:
      pin=0
    steppers[1] = getDirection(pin, 0, [pins[5], pins[7], pins[8], pins[9]])
  doSteps()
  pins[id] = 0;

def setPin(id):
  if pins[id]==1:
    return
  if id == 16:
    q.put(LIFT_MAZAK)
  elif id == 17:
    q.put(DROP_MAZAK)
  elif id < 5:
    steppers[0] = getDirection(id-1, 1, [pins[1], pins[2], pins[3], pins[4]])
  elif id == 14:
    q.put(END)
  else:
    pin = id-6
    if pin<0:
      pin=0

    steppers[1] = getDirection(pin, 1, [pins[5], pins[7], pins[8], pins[9]])
  doSteps()
  pins[id] = 1;
    
if __name__ == "__main__":
  open()
  test()
  wait()
