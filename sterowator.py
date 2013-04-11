#!/usr/bin/python2
#-*-coding: UTF-8 -*-
import math
import time

import os
import parapin
from parapin.CONST import *

from sys import argv

WHEEL_R = 18.0 #promien koła (w milimetrach)
ROBOT_R = 72.0 #odległosc między pisakiem a kołem - polowa odległosci rozstawu kol (w milimetrach)
REV_STEP = 1.0/512.0 #obrót osi silnika przy wykonaniu jednej serii kroków (seria 8 kroków)

MOTOR_DELAY = 1200.0 #opóźnienie między krokami w mikrosekundach

port = parapin.Port(LPT1, outmode=LP_PIN01|LP_DATA_PINS|LP_PIN16|LP_PIN17) # przejęcie obsługi portu i ustawienie pinów w tryb wyjścia

#zmienne z pinami
L_1 = port.get_pin(1) #Lewego silnika
L_2 = port.get_pin(2)
L_3 = port.get_pin(3)
L_4 = port.get_pin(4)

R_1 = port.get_pin(5) #Prawego silnika
R_2 = port.get_pin(7)
R_3 = port.get_pin(8)
R_4 = port.get_pin(9)

MAZAK_UP = port.get_pin(16) #mazakowego silnika
MAZAK_DOWN = port.get_pin(17)

usleep = lambda x: time.sleep(x/1000000.0) #definicja sleep w mikrosekundach

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
 
  
  def angle(self, other): #kąt między dwoma wektorami
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
	
    usleep(MOTOR_DELAY)
    
    L_3.set()
    
    R_4.clear()

    usleep(MOTOR_DELAY)

    L_4.clear()

    R_2.set()

    usleep(MOTOR_DELAY)

    L_2.set()

    R_1.clear()

    usleep(MOTOR_DELAY)

    L_3.clear()

    R_3.set()
    
    usleep(MOTOR_DELAY)

    L_1.set()
    
    R_2.clear()
    
    usleep(MOTOR_DELAY)

    L_2.clear()

    R_4.set()

    usleep(MOTOR_DELAY)

    L_4.set()

    R_3.clear()
    
    usleep(MOTOR_DELAY)

def spinCCW(steps): #funkcja odpowiedzialna za kręcenie się przeciwnie do ruchem wskazówek zegara (lewo) o zadaną liczbę kroków (serii po 8 kroków)
  for y in xrange(0,steps):
    L_1.set()
    L_2.clear()
    L_3.clear()
    L_4.set()
    
    R_1.set()
    R_2.clear()
    R_3.clear()
    R_4.set()

    usleep(MOTOR_DELAY)

    L_4.clear()

    R_4.clear()

    usleep(MOTOR_DELAY)

    L_2.set()

    R_2.set()
    
    usleep(MOTOR_DELAY)

    L_1.clear()
    
    R_1.clear()
    
    usleep(MOTOR_DELAY)

    L_3.set()
    
    R_3.set()
    
    usleep(MOTOR_DELAY)

    L_2.clear()
    
    R_2.clear()
    
    usleep(MOTOR_DELAY)

    L_4.set()

    R_4.set()

    usleep(MOTOR_DELAY)

    L_3.clear()
    
    R_3.clear()
    
    usleep(MOTOR_DELAY)

def spinCW(steps): #funkcja odpowiedzialna za kręcenie się zgodnie z ruchem wskazówek zegara (prawo) o zadaną liczbę kroków (serii po 8 kroków)
  for y in xrange(0,steps):
    L_1.clear()
    L_2.clear()
    L_3.clear()
    L_4.set()

    R_1.clear()
    R_2.clear()
    R_3.clear()
    R_4.set()
    
    usleep(MOTOR_DELAY)

    L_3.set()
    
    R_3.set()
    
    usleep(MOTOR_DELAY)

    L_4.clear()

    R_4.clear()

    usleep(MOTOR_DELAY)

    L_2.set()
    
    R_2.set()
    
    usleep(MOTOR_DELAY)

    L_3.clear()
    
    R_3.clear()
    
    usleep(MOTOR_DELAY)

    L_1.set()
    
    R_1.set()
    
    usleep(MOTOR_DELAY)

    L_2.clear()
    
    R_2.clear()
    
    usleep(MOTOR_DELAY)

    L_4.set()

    R_4.set()

    usleep(MOTOR_DELAY)

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
  
def liftMazak(): #podniesienie mazaka
  MAZAK_DOWN.clear()
  MAZAK_UP.set()
  
  time.sleep(0.1)
  
  MAZAK_UP.clear()
  
def dropMazak(): #opuszczenie mazaka
  MAZAK_UP.clear()
  MAZAK_DOWN.set()
  
  time.sleep(0.1)
  
  MAZAK_DOWN.clear()
  
def stepsForRotation(radians): #funkcja zwracająca przybliżoną do całkowitej liczbę kroków (8 krokowych ciągów) jakie trzeba wykonać by obrócić się o podany w radianach kąt
  deg = math.degrees(radians)
  
  return round(((2.0*math.pi*ROBOT_R*(deg/360.0))/(2.0*math.pi*WHEEL_R*REV_STEP)),0)
  
if __name__ == "__main__":
  inputfile = ''
  try:
    filename = argv[1]
  except IndexError:
    raise AssertionError('Podaj plik z danymi')
  
  p1 = Vector2D(0.0,0.0)
  p3 = Vector2D(0.0,-1.0)
  p2 = Vector2D(0.0,0.0)
  
  cleanPins()
  raw_imput("Podepnij zasilanie i wcisnij ENTER\n")
  
  fd = open(filename,'r')
  line = fd.readline()
  
  while line:
    if line.find('START') != -1:
      print("Początek rysowania")
    elif line.find('RYSUJ') != -1:
      dropMazak()
    elif line.find('PODNIES') != -1:
      liftMazak()
    elif line.find('KONIEC') != -1:
      print("Koniec rysowania")
    elif line.find('=') == -1:
      x = float(line[:line.find(' ')])
      y = float(line[line.find(' ')+1:-1])
      
      p2 = Vector2D(x,y)
      
      pom = Vector2D.angleFromPoints(p1,p2,p3)
      st = stepsForRotation(math.fabs(pom))
      
      if st > 0 :
        if pom > 0:
          spinCCW(st)
        elif pom < 0:
          spinCW(st)
      
      goStep()
      p3 = p1
      p1 = p2
      
    line = fd.readline()
    
  clearPins()
        
