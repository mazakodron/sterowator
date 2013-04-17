#!/usr/bin/env python
import os, code, sys

from sterowator import *

port = mazakodron.Port(simulator = False, lpt = False)

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

def DebugKeyboard(banner="Debugger started (CTRL-D to quit)"):

    # use exception trick to pick up the current frame
    try:
        raise None
    except:
        frame = sys.exc_info()[2].tb_frame.f_back

    # evaluate commands in current namespace
    namespace = frame.f_globals.copy()
    namespace.update(frame.f_locals)

    code.interact(banner=banner, local=namespace)

DebugKeyboard()
