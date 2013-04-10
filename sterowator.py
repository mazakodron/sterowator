#!/usr/bin/python2
#-*-coding: UTF-8 -*-
import math
import time
import os
import parapin
from parapin.CONST import *

WHEEL_R = 200.0 #promien koła (w milimetrach)
ROBOT_R = 520.0 #odległosc między pisakiem a kołem - polowa odległosci rozstawu kol (w milimetrach)
REV_STEP = 1.0/512.0 #obrót osi silnika przy wykonaniu jednej serii kroków (seria 8 kroków)

port = parapin.Port(LPT1, outmode=LP_PIN01|LP_DATA_PINS|LP_PIN16|LP_PIN17)

L_1 = parapin.Pin(LP_PIN01)
L_2 = parapin.Pin(LP_PIN02)
L_3 = parapin.Pin(LP_PIN03)
L_4 = parapin.Pin(LP_PIN04)

R_1 = parapin.Pin(LP_PIN05)
R_2 = parapin.Pin(LP_PIN07)
R_3 = parapin.Pin(LP_PIN08)
R_4 = parapin.Pin(LP_PIN09)

MAZAK_UP = parapin.Pin(LP_PIN16)
MAZAK_DOWN = parapin.Pin(LP_PIN17)

usleep = lambda x: time.sleep(x/1000000.0) #definicja sleep w mikrosekundach

class Vector2D ():
  def __init__(self, x, y):
    self.x = x
    self.y = y
 
  def __str__(self):
    return '[%f, %f]' % (self.x, self.y)
 
  def neg(self):
    return Vector2D(-self.x, -self.y)
 
  def add(self, other):
    x_sum = self.x + other.x
    y_sum = self.y + other.y
 
    return Vector2D(x_sum, y_sum)
 
  def sub(self, other):
    x_dif = self.x - other.x
    y_dif = self.y - other.y
 
    return Vector2D(x_dif, y_dif)
 
  def sqr_length(self):
    return self.x * self.x + self.y * self.y
 
  def length(self):
    return math.sqrt(self.sqr_length())
 
  def scale(self, factor):
    return Vector2D(self.x * factor, self.y * factor)
 
  def duplicate(self):
    return Vector2D(self.x, self.y)
 
  def normalize(self):
    v = self.duplicate()
    v.normalize_inplace()
    return v
 
  #def equals(self, other):
  #  return sqr(self.x - other.x) + sqr(self.y - other.y) &lt; ZERO_DISTANCE_SQR
 
  def perp_op(self):
    return Vector2D(-self.y, self.x)
 
  def dot(self, other):
    return self.x * other.x + self.y * other.y
 
  def perpdot(self, other):
    return - self.y * other.x + self.x * other.y
 
  def proj_on(self, other):
    scale_factor = self.dot(other)/other.sqr_length()
    new_vector = other.scale(scale_factor)
    return new_vector
 
  def perp_on(self, other):
    scale_factor = -(self.perpdot(other)/other.sqr_length())
    new_vector = other.scale(scale_factor)
 
    return new_vector
  
  def angle(self, other):
	rad = math.atan2( (- self.y * other.x + self.x * other.y), (self.x * other.x + self.y * other.y))
	
	return rad
	
  def angleFromPoints(now, next_p, prev):
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
	
    usleep(1000)
    
    #print(L_1," : 0")
    #print(L_2," : 0")
    L_3.set()
    #print(L_4," : 1")

    #print(R_1," : 1")
    #print(R_2," : 0")
    #print(R_3," : 0")
    R_4.clear()

    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 0")
    #print(L_3," : 1")
    L_4.clear()

    #print(R_1," : 1")
    R_2.set()
    #print(R_3," : 0")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 0")
    L_2.set()
    #print(L_3," : 1")
    #print(L_4," : 0")

    R_1.clear()
    #print(R_2," : 1")
    #print(R_3," : 0")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 1")
    L_3.clear()
    #print(L_4," : 0")

    #print(R_1," : 0")
    #print(R_2," : 1")
    R_3.set()
    #print(R_4," : 0")

    usleep(1000)

    L_1.set()
    #print(L_2," : 1")
    #print(L_3," : 0")
    #print(L_4," : 0")

    #print(R_1," : 0")
    R_2.clear()
    #print(R_3," : 1")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 1")
    L_2.clear()
    #print(L_3," : 0")
    #print(L_4," : 0")

    #print(R_1," : 0")
    #print(R_2," : 0")
    #print(R_3," : 1")
    R_4.set()

    usleep(1000)

    #print(L_1," : 1")
    #print(L_2," : 0")
    #print(L_3," : 0")
    L_4.set()

    #print(R_1," : 0")
    #print(R_2," : 0")
    R_3.clear()
    #print(R_4," : 1")

    usleep(1000)

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

    usleep(1000)

    #print(L_1," : 1")
    #print(L_2," : 0")
    #print(L_3," : 0")
    L_4.clear()

    #print(R_1," : 1")
    #print(R_2," : 0")
    #print(R_3," : 0")
    R_4.clear()

    usleep(1000)

    #print(L_1," : 1")
    L_2.set()
    #print(L_3," : 0")
    #print(L_4," : 0")

    #print(R_1," : 1")
    R_2.set()
    #print(R_3," : 0")
    #print(R_4," : 0")

    usleep(1000)

    L_1.clear()
    #print(L_2," : 1")
    #print(L_3," : 0")
    #print(L_4," : 0")

    R_1.clear()
    #print(R_2," : 1")
    #print(R_3," : 0")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 1")
    L_3.set()
    #print(L_4," : 0")

    #print(R_1," : 0")
    #print(R_2," : 1")
    R_3.set()
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 0")
    L_2.clear()
    #print(L_3," : 1")
    #print(L_4," : 0")

    #print(R_1," : 0")
    R_2.clear()
    #print(R_3," : 1")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 0")
    #print(L_3," : 1")
    L_4.set()

    #print(R_1," : 0")
    #print(R_2," : 0")
    #print(R_3," : 1")
    R_4.set()

    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 0")
    L_3.clear()
    #print(L_4," : 1")

    #print(R_1," : 0")
    #print(R_2," : 0")
    R_3.clear()
    #print(R_4," : 1")

    usleep(1000)

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
	
    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 0")
    L_3.set()
    #print(L_4," : 1")

    #print(R_1," : 0")
    #print(R_2," : 0")
    R_3.set()
    #print(R_4," : 1")
	
    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 0")
    #print(L_3," : 1")
    L_4.clear()

    #print(R_1," : 0")
    #print(R_2," : 0")
    #print(R_3," : 1")
    R_4.clear()

    usleep(1000)

    #print(L_1," : 0")
    L_2.set()
    #print(L_3," : 1")
    #print(L_4," : 0")

    #print(R_1," : 0")
    R_2.set()
    #print(R_3," : 1")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 0")
    #print(L_2," : 1")
    L_3.clear()
    #print(L_4," : 0")

    #print(R_1," : 0")
    #print(R_2," : 1")
    R_3.clear()
    #print(R_4," : 0")

    usleep(1000)

    L_1.set()
    #print(L_2," : 1")
    #print(L_3," : 0")
    #print(L_4," : 0")

    R_1.set()
    #print(R_2," : 1")
    #print(R_3," : 0")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 1")
    L_2.clear()
    #print(L_3," : 0")
    #print(L_4," : 0")

    #print(R_1," : 1")
    R_2.clear()
    #print(R_3," : 0")
    #print(R_4," : 0")

    usleep(1000)

    #print(L_1," : 1")
    #print(L_2," : 0")
    #print(L_3," : 0")
    L_4.set()

    #print(R_1," : 1")
    #print(R_2," : 0")
    #print(R_3," : 0")
    R_4.set()

    usleep(1000)

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
  
  time.sleep(0.5)
  
  MAZAK_UP.clear()
  
def dropMazak(): #opuszczenie mazaka
  MAZAK_UP.clear()
  MAZAK_DOWN.set()
  
  time.sleep(0.5)
  
  MAZAK_DOWN.clear()
  
def stepsForRotation(radians): #funkcja zwracająca przybliżoną do całkowitej liczbę kroków (8 krokowych ciągów) jakie trzeba wykonać by obrócić się o podany w radianach kąt
  deg = math.degrees(radians)
  
  return round(((2.0*math.pi*ROBOT_R*(deg/360.0))/(2.0*math.pi*WHEEL_R*REV_STEP)),0)
  
