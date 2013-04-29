#!/usr/bin/python
#-*-coding: UTF-8 -*-

class Pin():

  pin = None
  id = None
  port = None
  
  def __init__(self, port, id):
    self.id = id
    self.port = port
    if parapin:
      self.pin = port.get_pin(id)
  
  def set(self):
    if self.pin is not None:
      self.pin.set()
    if symulator:
      symulator.setPin(self.id)
  
  def clear(self):
    if self.pin is not None:
      self.pin.clear()
    if symulator:
      symulator.clearPin(self.id)
  
class Port():

  port = None
  
  def __init__(self, *args, **kargs):
    global parapin, symulator
    parapin = None
    symulator = None

    if kargs.get('lpt'):
      try:
        import parapin
        from parapin.CONST import LPT1, LP_PIN01, LP_DATA_PINS, LP_PIN14, LP_PIN16, LP_PIN17
      except ImportError:
        print("UWAGA: Nie można załadować modułu Parapin, komunikacja z robotem została wyłączona!")

    if kargs.get('simulator'):
      try:
        import symulator
      except ImportError:
        print("UWAGA: Nie można załadować modułu symulatora, wizualizacja została wyłączona!")

    if parapin:
      self.port = parapin.Port(LPT1, outmode=LP_PIN01|LP_DATA_PINS|LP_PIN14|LP_PIN16|LP_PIN17);

  def show(self):
    if symulator:
      symulator.open()

  def get_pin(self, id):
    return Pin(self.port, id)

  def wait(self):
    if symulator:
      symulator.wait()

  def close(self):
    if symulator:
      symulator.close()
