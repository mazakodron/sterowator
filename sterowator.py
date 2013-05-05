#!/usr/bin/python
#-*-coding: UTF-8 -*-
from __future__ import print_function
from optparse import OptionParser  
import math
import time
import os
import mazakodron

try:
  input = raw_input
except NameError:
  pass

from sys import argv

WHEEL_R = 18.0 #promien koła (w milimetrach)
ROBOT_R = 119.5 #odległosc między pisakiem a kołem - polowa odległosci rozstawu kol (w milimetrach)
REV_STEP = 1.0/4096.0 #obrót osi silnika przy wykonaniu jednego kroku

MOTOR_DELAY = 0.75 #opóźnienie między krokami w milisekundach

SPEED = 1.0
SPEED_MOD = lambda: 0 if SPEED==0 else 1/SPEED

mazak_lifted = False
backwards = False

single_rotation = 0
max_rotation = 0
total_rotation = 0

LEFT = []
RIGHT = []

msleep = lambda x: time.sleep((x/1000.0)*SPEED_MOD()) #definicja sleep w milisekundach
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

def goPinStep(engine, forward = True):
  prev = lambda pin: 3 if pin==0 else pin-1
  next = lambda pin: 0 if pin==3 else pin+1
  
  ran = range(0, 4)
  if not forward:
    ran = reversed(ran)
    next2 = next
    next = prev
    prev = next2
    
  for i in ran:
    if engine[i]['value']:
      if engine[next(i)]['value']:
        engine[i]['pin'].clear()
        engine[i]['value'] = 0
        return
      else:
        if not engine[prev(i)]['value']:
          engine[next(i)]['pin'].set()
          engine[next(i)]['value'] = 1
          return
  
  engine[0]['pin'].set()
  engine[0]['value'] = 1

def goStep(backwards = False): # funkcja odpowiedzialna za obrót silników o 5.625 stopni w celu jazdy do przodu, lewy silnik kręci się przeciwnie do ruchu wskazówek zegara, prawy zgodnie z ruchem wskazówek zegara
  
  for i in range(8):
    goPinStep(LEFT, backwards)
    goPinStep(RIGHT, not backwards)
    msleep(MOTOR_DELAY)
    #print(engine[0]['value'], engine[1]['value'], engine[2]['value'], engine[3]['value'])

        

def spin(steps, clockwise = True, prog = None): #funkcja odpowiedzialna za kręcenie się przeciwnie do ruchem wskazówek zegara (lewo) o zadaną liczbę kroków (serii po 8 kroków)
  for y in range(0,steps):
    if prog:
      prog(y, steps)
    for engine in (LEFT, RIGHT):
      goPinStep(engine, clockwise)
    msleep(MOTOR_DELAY)
    if clockwise:
      total_rotation = total_rotation + steps
    else:
      total_rotation = total_rotation - steps
    
def clearPins(): #wyczyszczenie wszystkich pinów
  for engine in (LEFT, RIGHT):
    for i in engine:
      i['value'] = 0
      i['pin'].clear()
  MAZAK_UP.clear()
  MAZAK_DOWN.clear()
  END.clear()

def liftMazak(t = 25): #podniesienie mazaka
  MAZAK_DOWN.clear()
  MAZAK_UP.set()

  msleep(t)

  MAZAK_UP.clear()

def dropMazak(t = 50): #opuszczenie mazaka
  MAZAK_UP.clear()
  for a in range(200):
    MAZAK_DOWN.set()
    msleep(0.5)
    MAZAK_DOWN.clear()
    msleep(3)
  #MAZAK_DOWN.set()

  #msleep(t)

  MAZAK_DOWN.clear()

def stepsForRotation(radians): #funkcja zwracająca przybliżoną do całkowitej liczbę kroków (8 krokowych ciągów) jakie trzeba wykonać by obrócić się o podany w radianach kąt
  deg = math.degrees(radians)

  return round(((2.0*math.pi*ROBOT_R*(deg/360.0))/(2.0*math.pi*WHEEL_R*REV_STEP)),0)

def progress(i, lines):
  return int(100*i/lines)

def countTime(filename):

  mazak_lifted = False
  backwards = False

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
        if pom > 0:
          pom = - math.pi + pom
        else:
          pom = math.pi + pom
        backwards = not backwards

      st = stepsForRotation(math.fabs(pom))

      time += (int(st)+8) * MOTOR_DELAY
      p3 = p1
      p1 = p2
    elif line.find('PODNIES') != -1:
      time += 100
    elif line.find('OPUSC') != -1:
      time += 100
    line = fd.readline()
    i+=1

  return time/800.0*SPEED_MOD()


def draw(filename):

  p1 = Vector2D(0.0,0.0)
  p3 = Vector2D(0.0,-1.0)
  p2 = Vector2D(0.0,0.0)

  dropRequest = False
  backwards = False
  
  single_rotation = stepsForRotation(2*math.pi)
  max_rotation = stepsForRotation(3*math.pi)

  clearPins()

  fd = open(filename,'r')
  line = fd.readline()
  i = 1

  start_time = int(time.time())
  try:
    while line:
      if line.find('START') != -1:
        print("[%3d%%] Początek rysowania" % progress(i,lines), end='\r')
        liftMazak(100)
        dropMazak(100)
        liftMazak()
        mazak_lifted = True
      elif line.find('OPUSC') != -1:
        print("[%3d%%] Żądanie opuszczenia mazaka...                                                         " % progress(i,lines), end='\r')
        if mazak_lifted:
          dropRequest = True
        mazak_lifted = False
      elif line.find('PODNIES') != -1:
        print("[%3d%%] Podnoszenie mazaka...                                                                 " % progress(i,lines), end='\r')
        if not mazak_lifted:
          liftMazak()
        mazak_lifted = True
        if abs(total_rotation) > max_rotation:
          pom = ( abs(total_rotation) - max_rotation ) // single_rotation
          spin( (1+pom) * single_rotation , total_rotation < 0)
      elif line.find('KONIEC') != -1:
        print("[%3d%%] Koniec rysowania                                                                       " % progress(i,lines))
        if not mazak_lifted:
          liftMazak()
        dropMazak()
        liftMazak()
        dropMazak()
        liftMazak(100)
        mazak_lifted = True
        END.set()
        break
      elif line.find('=') == -1:
        x = float(line[:line.find(' ')])
        y = float(line[line.find(' ')+1:-1])
        p2 = Vector2D(x,y)

        pom = Vector2D.angleFromPoints(p1,p2,p3)

        
        if abs(pom) > math.pi/2:
          if pom > 0:
            pom = - math.pi + pom
          else:
            pom = math.pi + pom
          backwards = not backwards

        st = stepsForRotation(math.fabs(pom))

        etaLeft = int(eta - time.time() + start_time)
        if etaLeft < 0:
          etaLeft = 0
        print("[%3d%%] %s do %s do punktu %.2f %.2f (ETA: %dm)                                               " % (progress(i,lines), 'Jadę' if mazak_lifted else 'Rysuję', 'tyłu' if backwards else 'przodu', x, y, int(etaLeft/60)), end='\r')

        if st > 0 :
          def prog(a, max):
            print("[%3d%%] %s do %s do punktu %.2f %.2f [obrót: %.2f/%d (%d%%)] (ETA: %dm)" % (progress(i,lines), 'Jadę' if mazak_lifted else 'Rysuję', 'tyłu' if backwards else 'przodu', x, y, pom, int(st), int(100*a/max), int(etaLeft/60)), end='\r')
          spin(int(st), pom < 0, prog)
        #print (" - step                                            ", end='\r') # yes, it's ugly :D
        if dropRequest:
          print("[%3d%%] Opuszczanie mazaka...                                                                   " % progress(i,lines), end='\r')
          dropMazak()
          dropRequest = False
        goStep(backwards)
        p3 = p1
        p1 = p2

      line = fd.readline()
      i+=1

  except KeyboardInterrupt:
    print("[%3d%%] Czyszczenie pinów...                                                                       " % progress(i,lines)) # uuuuglyyyy
    liftMazak(500)
    clearPins()
    raise KeyboardInterrupt

  clearPins()
  time_elapsed = int(time.time() - start_time)
  print("Upłynęło: %dm%s%ds" % (int(time_elapsed/60), '0' if time_elapsed%60<10 else '', time_elapsed%60))
  return time_elapsed

if __name__ == "__main__":

  print("Mazakodron 3000 - Sterowator 2000")

  inputfile = ''

  parser = OptionParser()
  parser.add_option("-s", "--speed", dest="speed", metavar="FLOAT", help="przyśpiesza czasy oczekiwania o podany mnożnik")
  parser.add_option("", "--disable-simulator", dest="simulator", action="store_true", default=False, help="wyłącza symulator Mazakodronu")
  parser.add_option("", "--disable-lpt", dest="lpt", action="store_true", help="wyłącza komunikację z robotem po porcie LPT")
  options, args = parser.parse_args()

  if options.speed:
    SPEED = float(options.speed)

  try:
    filename = args[0]
  except IndexError:
    raise AssertionError('Podaj plik z danymi')

  with open(filename) as f:
    for i, l in enumerate(f):
      pass
  lines = i

  eta = countTime(filename)
  print("Plik %s, ETA: %dm%s%ds" % (filename, int(eta/60), '0' if eta%60<10 else '', eta%60))

  port = mazakodron.Port(simulator = not options.simulator, lpt = not options.lpt)
  #lpt.Port(LPT1, outmode=LP_PIN01|LP_DATA_PINS|LP_PIN16|LP_PIN17) # przejęcie obsługi portu i ustawienie pinów w tryb wyjścia

  #zmienne z pinami
  L_1 = port.get_pin(9) #Lewego silnika
  L_2 = port.get_pin(8)
  L_3 = port.get_pin(7)
  L_4 = port.get_pin(5)

  R_1 = port.get_pin(4) #Prawego silnika
  R_2 = port.get_pin(3)
  R_3 = port.get_pin(2)
  R_4 = port.get_pin(1)
  
  LEFT.append({'pin': L_1, 'value': 0})
  LEFT.append({'pin': L_2, 'value': 0})
  LEFT.append({'pin': L_3, 'value': 0})
  LEFT.append({'pin': L_4, 'value': 0})
  RIGHT.append({'pin': R_1, 'value': 0})
  RIGHT.append({'pin': R_2, 'value': 0})
  RIGHT.append({'pin': R_3, 'value': 0})
  RIGHT.append({'pin': R_4, 'value': 0})
  
  
  MAZAK_UP = port.get_pin(16) #mazakowego silnika
  MAZAK_DOWN = port.get_pin(17)

  END = port.get_pin(14)


  clearPins()
  input("Ustaw robota w lewym górnym rogu kartki, podepnij zasilanie i wcisnij ENTER")

  port.show()
  draw(filename)

  port.wait()
