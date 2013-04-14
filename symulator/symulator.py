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

  def run(self):
    app = QApplication(sys.argv)

    # Create the QML user interface.
    view = QDeclarativeView()
    view.setSource(QUrl('mazakodron.qml'))
    view.setResizeMode(QDeclarativeView.SizeRootObjectToView)

    rootObject = view.rootObject()
    self.rootObject = rootObject

    view.setGeometry(0, 0, 800, 600)
    view.show()

    timer = QTimer()
    timer.start(1000/60) # 60FPS
    timer.timeout.connect(self.process)

    sys.exit(app.exec_());

thread = Interface()
thread.start()

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

test()
thread.join()
