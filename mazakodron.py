#!/usr/bin/python
#-*-coding: UTF-8 -*-

try:
  import parapin
  from parapin.CONST import *
except ImportError:
  parapin = None
  print("UWAGA: Nie można załadować modułu Parapin, komunikacja z robotem została wyłączona!")

try:
  import symulator
except ImportError:
  symulator = None
  print("UWAGA: Nie można załadować modułu symulatora, wizualizacja została wyłączona!")
  
class Pin():

  pin = None
  id = None
  
  def __init__(self, id):
    self.id = id
    if parapin:
      self.pin = Pin(id)
  
  def set(self):
    if self.pin:
      pin.set()
    if symulator:
      symulator.setPin(self.id)
  
  def clear(self):
    if self.pin:
      pin.clear()
    if symulator:
      symulator.clearPin(self.id)
  
class Port():

  port = None
  
  def __init__(self):
    if parapin:
      self.port = Port(LPT1, outmode=LP_PIN01|LP_DATA_PINS|LP_PIN14|LP_PIN16|LP_PIN17);

  def show(self):
    if symulator:
      symulator.open()

  def get_pin(self, id):
    return Pin(id)

  def wait(self):
    if symulator:
      symulator.wait()

  def close(self):
    if symulator:
      symulator.close()