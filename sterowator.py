#!/usr/bin/python2
#-*-coding: UTF-8 -*-
from __future__ import print_function
import math
import time
import os

try:
  import parapin
  from parapin.CONST import *
except ImportError:
  print("UWAGA: Nie można załadować modułu Parapin, zostanie użyta imitacja!")
  import parapin_mock as parapin
  from parapin_mock import *

from sys import argv

WHEEL_R = 18.0 #promien koła (w milimetrach)
ROBOT_R = 119.5 #odległosc między pisakiem a kołem - polowa odległosci rozstawu kol (w milimetrach)
REV_STEP = 1.0/512.0 #obrót osi silnika przy wykonaniu jednej serii kroków (seria 8 kroków)

MOTOR_DELAY = 1.0 #opóźnienie między krokami w milisekundach

port = parapin.Port(LPT1, outmode=LP_PIN01|LP_DATA_PINS|LP_PIN16|LP_PIN17) # przejęcie obsługi portu i ustawienie pinów w tryb wyjścia

mazak_lifted = False
backwards = False

#zmienne z pinami
L_1 = port.get_pin(9) #Lewego silnika
L_2 = port.get_pin(8)
L_3 = port.get_pin(7)
L_4 = port.get_pin(5)

R_1 = port.get_pin(4) #Prawego silnika
R_2 = port.get_pin(3)
R_3 = port.get_pin(2)
R_4 = port.get_pin(1)

MAZAK_UP = port.get_pin(16) #mazakowego silnika
MAZAK_DOWN = port.get_pin(17)

msleep = lambda x: time.sleep(x/1000.0) #definicja sleep w milisekundach
#msleep = lambda x: x

class Vector2D (): #definicja klasy wektorów dwuwymiarowych, potrzebna do oblicznia kątów obrotu robota
  def __init__(self, x, y):
    self.x = x
    self.y = y
 
  def __str__(self):
    return '[%f, %f]' % (self.x, self.y)
 
  def neg(self): #negacja wektorów
    return Vector2D(-self.x, -self.y)
 
  def add(self, other): #dodawanie wektorów
    x_sum = self.x + other.x
    y_sum = self.y + other.y
 
    return Vector2D(x_sum, y_sum)
 
  def sub(self, other): #odejmowanie wektorów
    x_dif = self.x - other.x
    y_dif = self.y - other.y
 
    return Vector2D(x_dif, y_dif)
 
  
  def angle(self, other): #kąt między dwoma wektorami, 
	rad = math.atan2( (- self.y * other.x + self.x * other.y), (self.x * other.x + self.y * other.y))
	
	return rad
	
  def angleFromPoints(now, next_p, prev): #kąt między wektorami utworzonymi z 3 punktów
	v0 = Vector2D.neg(Vector2D.sub(prev, now))
	v1 = Vector2D.sub(next_p, now)
	
	return Vector2D.angle(v0, v1)

  
def goStep(): # funkcja odpowiedzialna za obrót silników o 5.625 stopni w celu jazdy do przodu, lewy silnik kręci się przeciwnie do ruchu wskazówek zegara, prawy zgodnie z ruchem wskazówek zegara
  for x in range(8):
    L_1.clear()
    L_2.clear()
    L_3.clear()
    L_4.set()
    
    R_1.set()
    R_2.clear()
    R_3.clear()
    R_4.set()
	
    msleep(MOTOR_DELAY)
    
    L_3.set()
    
    R_4.clear()

    msleep(MOTOR_DELAY)

    L_4.clear()

    R_2.set()

    msleep(MOTOR_DELAY)

    L_2.set()

    R_1.clear()

    msleep(MOTOR_DELAY)

    L_3.clear()

    R_3.set()
    
    msleep(MOTOR_DELAY)

    L_1.set()
    
    R_2.clear()
    
    msleep(MOTOR_DELAY)

    L_2.clear()

    R_4.set()

    msleep(MOTOR_DELAY)

    L_4.set()

    R_3.clear()
    
    msleep(MOTOR_DELAY)

def goStepBackwards(): # funkcja odpowiedzialna za obrót silników o 5.625 stopni w celu jazdy do tyłu, lewy silnik kręci się zgodnie z ruchem wskazówek zegara, prawy przeciwnie do ruchu wskazówek zegara

  for x in range(8):
    R_1.clear()
    R_2.clear()
    R_3.clear()
    R_4.set()

    L_1.set()
    L_2.clear()
    L_3.clear()
    L_4.set()

    msleep(MOTOR_DELAY)

    R_3.set()

    L_4.clear()

    msleep(MOTOR_DELAY)

    R_4.clear()

    L_2.set()

    msleep(MOTOR_DELAY)

    R_2.set()

    L_1.clear()

    msleep(MOTOR_DELAY)

    R_3.clear()

    L_3.set()

    msleep(MOTOR_DELAY)

    R_1.set()

    L_2.clear()

    msleep(MOTOR_DELAY)

    R_2.clear()

    L_4.set()

    msleep(MOTOR_DELAY)

    R_4.set()

    L_3.clear()

    msleep(MOTOR_DELAY)

def spinCW(steps, prog = None): #funkcja odpowiedzialna za kręcenie się przeciwnie do ruchem wskazówek zegara (lewo) o zadaną liczbę kroków (serii po 8 kroków)
  for y in xrange(0,steps):
    if prog:
      prog(y, steps)
    L_1.set()
    L_2.clear()
    L_3.clear()
    L_4.set()
    
    R_1.set()
    R_2.clear()
    R_3.clear()
    R_4.set()

    msleep(MOTOR_DELAY)

    L_4.clear()

    R_4.clear()

    msleep(MOTOR_DELAY)

    L_2.set()

    R_2.set()
    
    msleep(MOTOR_DELAY)

    L_1.clear()
    
    R_1.clear()
    
    msleep(MOTOR_DELAY)

    L_3.set()
    
    R_3.set()
    
    msleep(MOTOR_DELAY)

    L_2.clear()
    
    R_2.clear()
    
    msleep(MOTOR_DELAY)

    L_4.set()

    R_4.set()

    msleep(MOTOR_DELAY)

    L_3.clear()
    
    R_3.clear()
    
    msleep(MOTOR_DELAY)

def spinCCW(steps, prog = None): #funkcja odpowiedzialna za kręcenie się zgodnie z ruchem wskazówek zegara (prawo) o zadaną liczbę kroków (serii po 8 kroków)
  for y in xrange(0,steps):
    if prog:
      prog(y, steps)
    L_1.clear()
    L_2.clear()
    L_3.clear()
    L_4.set()

    R_1.clear()
    R_2.clear()
    R_3.clear()
    R_4.set()
    
    msleep(MOTOR_DELAY)

    L_3.set()
    
    R_3.set()
    
    msleep(MOTOR_DELAY)

    L_4.clear()

    R_4.clear()

    msleep(MOTOR_DELAY)

    L_2.set()
    
    R_2.set()
    
    msleep(MOTOR_DELAY)

    L_3.clear()
    
    R_3.clear()
    
    msleep(MOTOR_DELAY)

    L_1.set()
    
    R_1.set()
    
    msleep(MOTOR_DELAY)

    L_2.clear()
    
    R_2.clear()
    
    msleep(MOTOR_DELAY)

    L_4.set()

    R_4.set()

    msleep(MOTOR_DELAY)

def clearPins(): #wyczyszczenie wszystkich pinów
  L_1.clear()
  L_2.clear()
  L_3.clear()
  L_4.clear()
  R_1.clear()
  R_2.clear()
  R_3.clear()
  R_4.clear()
  MAZAK_UP.clear()
  MAZAK_DOWN.clear()
  
def liftMazak(t = 25): #podniesienie mazaka
  MAZAK_DOWN.clear()
  MAZAK_UP.set()
  
  msleep(t)
  
  MAZAK_UP.clear()
  
def dropMazak(t = 50): #opuszczenie mazaka
  MAZAK_UP.clear()
  MAZAK_DOWN.set()
  
  msleep(t)
  
  MAZAK_DOWN.clear()
  
def stepsForRotation(radians): #funkcja zwracająca przybliżoną do całkowitej liczbę kroków (8 krokowych ciągów) jakie trzeba wykonać by obrócić się o podany w radianach kąt
  deg = math.degrees(radians)
  
  return round(((2.0*math.pi*ROBOT_R*(deg/360.0))/(2.0*math.pi*WHEEL_R*REV_STEP)),0)

def progress(i, lines):
  return int(100*i/lines)

def countTime(filename):

  mazak_lifted = False
  
  p1 = Vector2D(0.0,0.0)
  p3 = Vector2D(0.0,-1.0)
  p2 = Vector2D(0.0,0.0)
  
  fd = open(filename,'r')
  line = fd.readline()
  i = 1

  time = 0

  while line:
    if line.find(' ') != -1:
      x = float(line[:line.find(' ')])
      y = float(line[line.find(' ')+1:-1])
      p2 = Vector2D(x,y)

      pom = Vector2D.angleFromPoints(p1,p2,p3)

      if abs(pom) > math.pi/2:
        pom -= math.pi/2 * abs(pom)/pom
        pom *= -1
        backwards = True
      else:
        backwards = False

      st = stepsForRotation(math.fabs(pom))

      time += st * 8 * MOTOR_DELAY
      time += 64 * MOTOR_DELAY
      p3 = p1
      p1 = p2
    elif line.find('PODNIES') != -1:
      time += 25
    elif line.find('OPUSC') != -1:
      time += 50
    line = fd.readline()
    i+=1

  time += 500
  return time*1.125/1000.0


def draw(filename):

  p1 = Vector2D(0.0,0.0)
  p3 = Vector2D(0.0,-1.0)
  p2 = Vector2D(0.0,0.0)
  
  dropRequest = False
  
  clearPins()

  fd = open(filename,'r')
  line = fd.readline()
  i = 1

  start_time = int(time.time())
  try:
    while line:
      if line.find('START') != -1:
        print("[%3d%%] Początek rysowania" % progress(i,lines))
        liftMazak(100)
        dropMazak(100)
        liftMazak()
        mazak_lifted = True
      elif line.find('OPUSC') != -1:
        print("[%3d%%] Żądanie opuszczenia mazaka..." % progress(i,lines))
        if mazak_lifted:
          dropRequest = True
        mazak_lifted = False
      elif line.find('PODNIES') != -1:
        print("[%3d%%] Podnoszenie mazaka..." % progress(i,lines))
        if not mazak_lifted:
          liftMazak()
        mazak_lifted = True
      elif line.find('KONIEC') != -1:
        print("[%3d%%] Koniec rysowania" % progress(i,lines))
        if not mazak_lifted:
          liftMazak()
        dropMazak()
        liftMazak()
        dropMazak()
        liftMazak(100)
        mazak_lifted = True
        break
      elif line.find('=') == -1:
        x = float(line[:line.find(' ')])
        y = float(line[line.find(' ')+1:-1])
        p2 = Vector2D(x,y)

        pom = Vector2D.angleFromPoints(p1,p2,p3)

        if abs(pom) > math.pi/2:
          pom -= math.pi/2 * abs(pom)/pom
          pom *= -1
          backwards = True
        else:
          backwards = False

        st = stepsForRotation(math.fabs(pom))

        etaLeft = int(eta - time.time() + start_time)
        if etaLeft < 0:
          etaLeft = 0
        print("[%3d%%] %s do %s do punktu %.2f %.2f (ETA: %dm)" % (progress(i,lines), 'Jadę' if mazak_lifted else 'Rysuję', 'tyłu' if backwards else 'przodu', x, y, int(etaLeft/60)))

        if st > 0 :
          def prog(i, max):
            print(" - kroków: %d*8=%d, kąt: %.2f (%d%%)" % (st, st*8, pom, int(100*i/max)), end='\r')
          if pom > 0:
            spinCCW(int(st), prog)
          elif pom < 0:
            spinCW(int(st), prog)
        print (" - step                                            ", end='\r') # yes, it's ugly :D
        if dropRequest:
          print("[%3d%%] Opuszczanie mazaka..." % progress(i,lines))
          dropMazak()
          dropRequest = False
        if backwards:
          goStepBackwards()
        else:
          goStep()
        p3 = p1
        p1 = p2

      line = fd.readline()
      i+=1

  except KeyboardInterrupt:
    print("Czyszczenie pinów...                                ") # uuuuglyyyy
    liftMazak(100)
    clearPins()
    raise KeyboardInterrupt

  clearPins()
  time_elapsed = int(time.time() - start_time)
  print("Upłynęło: %dm%s%ds" % (int(time_elapsed/60), '0' if time_elapsed%60<10 else '', time_elapsed%60))
  return time_elapsed
 
if __name__ == "__main__":

  print("Mazakodron 3000 - Sterowator 2000")

  inputfile = ''
  try:
    filename = argv[1]
  except IndexError:
    raise AssertionError('Podaj plik z danymi')

  with open(filename) as f:
    for i, l in enumerate(f):
      pass
  lines = i  

  eta = countTime(filename)
  print("Plik %s, ETA: %dm%s%ds" % (filename, int(eta/60), '0' if eta%60<10 else '', eta%60))
  
  clearPins()
  raw_input("Ustaw robota w lewym górnym rogu kartki, podepnij zasilanie i wcisnij ENTER")
  
  draw(filename)
