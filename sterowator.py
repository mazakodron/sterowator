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

MOTOR_DELAY = 1.5 #opóźnienie między krokami w milisekundach

SPEED = 1.0
SPEED_MOD = lambda: 0 if SPEED==0 else 1/SPEED

mazak_lifted = False  
backwards = False

single_rotation = 0
max_rotation = 0
total_rotation = 0

LEFT = []   #tablica pinów i wartości lewego silnika
RIGHT = []  #tablica pinów i wartości prawego silnika

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

def goPinStep(engine, forward = True):    #przejście na pinach silnika w kolejny stan / wykonanie pojedyńczego kroku
  prev = lambda pin: 3 if pin==0 else pin-1  #numer poprzedniego pinu
  next = lambda pin: 0 if pin==3 else pin+1  #numer następnego pinu
  
  ran = range(0, 4)
  if not forward:  #odwracanie kolejności pinów jeżeli silnik ma się kręcić do tył
    ran = reversed(ran)
    next2 = next
    next = prev
    prev = next2
    
  for i in ran:  # przejście do kolejnego stanu w cyklu kroków
    if engine[i]['value']:
      if engine[next(i)]['value']: #jeżeli mamy dwa kolejne piny ustawione
        engine[i]['pin'].clear()   #czyszczenie pierwszego z nich
        engine[i]['value'] = 0
        return
      else:
        if not engine[prev(i)]['value']: #jeżeli tylko jeden pin jest zapalony
          engine[next(i)]['pin'].set()   #zapalenie kolejnego w cyklu
          engine[next(i)]['value'] = 1
          return
  
  engine[0]['pin'].set() #ustawienie stanu wysokiego na pinie 0 jeżeli wcześniej pin były wyczyszczone
  engine[0]['value'] = 1

def goStep(backwards = False): 
  '''
    funkcja odpowiedzialna za przejazd robota do przodu o jedną jednostkę odległości obrót silników o ~0,7 stopni w przeciwnych kierunkach 
    odpowiada to wykonaniu serii 8 kroków
    jeżeli jedziemy do przodu lewy silnik kręci się w kierunku przeciwnym do ruchu wskazówek zegara a prawy zgodnie z nim
    przy jeździe do tył mamy odwrotną sytuację
  '''
  for i in range(8):
    goPinStep(LEFT, backwards)   
    goPinStep(RIGHT, not backwards)
    msleep(MOTOR_DELAY) # opóźnienie między kolejnymi krokami
    #print(engine[0]['value'], engine[1]['value'], engine[2]['value'], engine[3]['value'])

        

def spin(steps, clockwise = True, prog = None): 
  '''
    funkcja odpowiedzialna za kręcenie się robota w miejscu o zadaną liczbę kroków
  '''
  global total_rotation
  for y in range(0,int(steps)):
    if prog:
      prog(y, steps)  #funkcja wypisująca postęp obrotu
    for engine in (LEFT, RIGHT):  #dla obu silników wykonuje się krok w tym samym kierunku
      goPinStep(engine, clockwise)
    msleep(MOTOR_DELAY) #przerwa między krokami
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

def dropMazak(t = 50): #opuszczenie mazaka za pomocą serii krótkich sygnałów, pozwala to ogranicyć gwałtowność opuszczania i zapobiec odbijaniu mazaka od kartki
  MAZAK_UP.clear()
  for a in range(200):
    MAZAK_DOWN.set()
    msleep(0.5)
    MAZAK_DOWN.clear()
    msleep(3)
  #MAZAK_DOWN.set()

  #msleep(t)

  MAZAK_DOWN.clear()

def stepsForRotation(radians): #funkcja zwracająca przybliżoną do całkowitej liczbę kroków jakie trzeba wykonać by obrócić się o podany w radianach kąt
  deg = math.degrees(radians)

  return round(((2.0*math.pi*ROBOT_R*(deg/360.0))/(2.0*math.pi*WHEEL_R*REV_STEP)),0)

def progress(i, lines):  #funkcja obliczająca postęp rysowania obrazka - procent linii przetworzonych w stosunku do wszystkich linii pliku wejściowego 
  return int(100*i/lines)

def countTime(filename):  #funkcja prekalkująca całkowity czas rysowania - przetwarza cały plik sumując przypisane czasy wykonania operacji

  mazak_lifted = False #zmienna pamiętająca stan mazaka
  backwards = False #zmienna określająca kierunek jazdy

  p1 = Vector2D(0.0,0.0) #akutalny punkt
  p3 = Vector2D(0.0,-1.0) #poprzedni punkt
  p2 = Vector2D(0.0,0.0) #następny punkt 

  fd = open(filename,'r') #otwarcie pliku
  line = fd.readline()
  i = 1

  time = 0 # zainicjowanie zmiennej liczącej czas wykonania

  while line: #dla każdej linii:
    if line.find(' ') != -1: #jeżeli znaleziono współrzędne
      x = float(line[:line.find(' ')]) #wczytanie współrzędnnej x
      y = float(line[line.find(' ')+1:-1]) #wczytanie współrzędnej y
      p2 = Vector2D(x,y) 

      pom = Vector2D.angleFromPoints(p1,p2,p3) #przeliczenie kąta między aktualnym kierunkiem jazdy a docelowym

      if abs(pom) > math.pi/2: #jeżeli obrót byłby większy niż kąt prosty - zmiana kierunku jazdy i przeliczenie kąta na nowy
        if pom > 0:
          pom = - math.pi + pom
        else:
          pom = math.pi + pom
        backwards = not backwards #zmiana kierunku jazdy

      st = stepsForRotation(math.fabs(pom)) #przeliczenie kąta obrotu na kroki

      time += (int(st)+8) * MOTOR_DELAY #dodanie odpowiedniego czasu wykonywania obrotu do całkowitego czasu wykonania rysunku
      p3 = p1
      p1 = p2
    elif line.find('PODNIES') != -1:
      time += 100 #dodanie czasu podnoszenia mazaka
    elif line.find('OPUSC') != -1:
      time += 100 #dodanie czasu opuszczania mazaka
    line = fd.readline()
    i+=1

  return time/800.0*SPEED_MOD() #zwracamy obliczony czas  - przeskalowany odpowiednio do ustawionej szybkości robota


def draw(filename):  #funkcja rysująca

  global single_rotation, max_rotation, total_rotation

  p1 = Vector2D(0.0,0.0) #punkt aktualny
  p3 = Vector2D(0.0,-1.0) #punkt poprzedzający
  p2 = Vector2D(0.0,0.0) #punkt docelowy

  dropRequest = False #zmienna zapamiętująca rządanie opuszczenia mazaka
  backwards = False #zmienna określająca kierunek jazdy
  
  single_rotation = stepsForRotation(2*math.pi)
  max_rotation = stepsForRotation(3*math.pi)

  clearPins()

  fd = open(filename,'r')
  line = fd.readline()
  i = 1

  start_time = int(time.time())
  try:
    while line: #dla każdej linii pliku wejściwego wykonaj operacje odpowiadające poleceniom
      if line.find('START') != -1: #sygnalizuje początek rysowania - podnosi mazak na dobry początek
        print("[%3d%%] Początek rysowania" % progress(i,lines), end='\r')
        liftMazak(100)
        dropMazak(100)
        liftMazak()
        mazak_lifted = True
      elif line.find('OPUSC') != -1: #zapamiętuje żądanie opuszczenia mazaka - opuści go dopiero po wykonaniu obrotu robota
        print("[%3d%%] Żądanie opuszczenia mazaka...                                                         " % progress(i,lines), end='\r')
        if mazak_lifted:
          dropRequest = True
        mazak_lifted = False
      elif line.find('PODNIES') != -1: #podnosi mazak
        print("[%3d%%] Podnoszenie mazaka...                                                                 " % progress(i,lines), end='\r')
        if not mazak_lifted:
          liftMazak()
        mazak_lifted = True
        #if abs(total_rotation) > max_rotation:
        #  pom = ( abs(total_rotation) - max_rotation ) // single_rotation
        #  def prog(a,max):
        #    print("[%3d%%] Rozplątywanie kabli... [%d%%] (ETA: %dm)                     " % (progress(i,lines), int(100*a/max), int(etaLeft/60)), end='\r')
        #  spin( int((1+pom) * single_rotation) , total_rotation < 0, prog)
      elif line.find('KONIEC') != -1: #stwierdza koniec rysowania - sygnalizuje to serią ruchów mazakiem
        print("[%3d%%] Koniec rysowania                                                                       " % progress(i,lines))
        if not mazak_lifted:
          liftMazak()
        dropMazak()
        liftMazak()
        dropMazak()
        liftMazak(100)
        mazak_lifted = True
        END.set() #ustawia pin sygnalizujący koniec rysowania - sygnał dla symulatora
        break
      elif line.find('=') == -1: #jeżeli to współrzędne punktu
        x = float(line[:line.find(' ')]) #wczytuje współrzędną x
        y = float(line[line.find(' ')+1:-1]) #wczytuje współrzędną y
        p2 = Vector2D(x,y) #ustawia wektor punktu docelowego

        pom = Vector2D.angleFromPoints(p1,p2,p3) # oblicza kąt między wektorami punktów - kąt między aktualnym kierunkiem jazdy a docelowym

        
        if abs(pom) > math.pi/2: #jeżeli obrót byłby większy niż kąt prosty odwracamy kierunek jazdy i przeliczamy kąt obrotu na nowy
          if pom > 0: 
            pom = - math.pi + pom
          else:
            pom = math.pi + pom
          backwards = not backwards #odwrócenie kierunku jazdy

        st = stepsForRotation(math.fabs(pom)) # obliczenie ilości kroków potrzebnych do wykonania obrotu 

        etaLeft = int(eta - time.time() + start_time) #oszacowanie czasu do końca rysowania
        if etaLeft < 0:
          etaLeft = 0
        print("[%3d%%] %s do %s do punktu %.2f %.2f (ETA: %dm)                                               " % (progress(i,lines), 'Jadę' if mazak_lifted else 'Rysuję', 'tyłu' if backwards else 'przodu', x, y, int(etaLeft/60)), end='\r')

        if st > 0 : #jeżeli wykonywany jest choć jednen krok (kąt obrotu może być za mały by mieć znaczenie)
          def prog(a, max):
            print("[%3d%%] %s do %s do punktu %.2f %.2f [obrót: %.2f/%d (%d%%)] (ETA: %dm)      " % (progress(i,lines), 'Jadę' if mazak_lifted else 'Rysuję', 'tyłu' if backwards else 'przodu', x, y, pom, int(st), int(100*a/max), int(etaLeft/60)), end='\r')
          spin(int(st), pom < 0, prog)
        #print (" - step                                            ", end='\r') # yes, it's ugly :D
        if dropRequest: #jeżeli nastąpiło wcześniej rządanie opuszczenia mazaka opuszczamy go
          print("[%3d%%] Opuszczanie mazaka...                                                                   " % progress(i,lines), end='\r')
          dropMazak()
          dropRequest = False
        goStep(backwards) #przejazd o jedną jednostkę odległości
        p3 = p1 # zapamiętanie wcześniej akutalnej pozycji jako poprzednią
        p1 = p2 #zapamiętanie pozycji docelowej jako aktualną

      line = fd.readline() #wczytanie kolejnej linii
      i+=1

  except KeyboardInterrupt: #wyczyszczenie pinów w wypadku zgłoszenia przerwania z klawiatury (CTRL + C) przed rzeczywistym przerwaniem działania programu
    print("[%3d%%] Czyszczenie pinów...                                                                       " % progress(i,lines)) # uuuuglyyyy
    liftMazak(500)
    clearPins()
    raise KeyboardInterrupt
# po skończeniu pliku
  clearPins() #wyczyszczenie pinów 
  time_elapsed = int(time.time() - start_time)
  print("Upłynęło: %dm%s%ds" % (int(time_elapsed/60), '0' if time_elapsed%60<10 else '', time_elapsed%60)) #wypisanie rzeczywistego czasu rysowania
  return time_elapsed 

if __name__ == "__main__":

  print("Mazakodron 3000 - Sterowator 2000")

  inputfile = ''

  parser = OptionParser() #parer opcji dodatkowch
  parser.add_option("-s", "--speed", dest="speed", metavar="FLOAT", help="przyśpiesza czasy oczekiwania o podany mnożnik")
  parser.add_option("", "--disable-simulator", dest="simulator", action="store_true", default=False, help="wyłącza symulator Mazakodronu")
  parser.add_option("", "--disable-lpt", dest="lpt", action="store_true", help="wyłącza komunikację z robotem po porcie LPT")
  options, args = parser.parse_args()

  if options.speed: #zmiana domyślnej prędkości jeżeli podano przy uruchamianiu odpowiednią opcję
    SPEED = float(options.speed)

  try:
    filename = args[0]
  except IndexError:
    raise AssertionError('Podaj plik z danymi')

  with open(filename) as f:
    for i, l in enumerate(f):
      pass
  lines = i

  eta = countTime(filename) #obliczenie szacowanego czasu rysowania
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
  
  LEFT.append({'pin': L_1, 'value': 0}) #przepisanie pinów do tablicy trzmającej również aktualne wartości pinów
  LEFT.append({'pin': L_2, 'value': 0})
  LEFT.append({'pin': L_3, 'value': 0})
  LEFT.append({'pin': L_4, 'value': 0})
  RIGHT.append({'pin': R_1, 'value': 0})
  RIGHT.append({'pin': R_2, 'value': 0})
  RIGHT.append({'pin': R_3, 'value': 0})
  RIGHT.append({'pin': R_4, 'value': 0})
  
  
  MAZAK_UP = port.get_pin(16) #mazakowego silnika
  MAZAK_DOWN = port.get_pin(17)

  END = port.get_pin(14) #port sygnalizujący zakończenie rysowania - wykorzystywany w symulatorze


  clearPins()
  input("Ustaw robota w lewym górnym rogu kartki, podepnij zasilanie i wcisnij ENTER")

  port.show()
  draw(filename) #rozpoczęcie rysowania pliku

  port.wait()
