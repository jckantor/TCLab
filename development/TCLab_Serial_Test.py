#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 14:56:13 2018

@author: jeff
"""

import sys
import time
import serial
from serial.tools import list_ports
from math import ceil, floor
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython import display
        
class TCLab(object):

    def __init__(self, port=None, baud=9600):
        #if (sys.platform == 'darwin') and not port:
        #    port = '/dev/tty.wchusbserial1410'
        #else:
        port = self.findPort()
        print('Opening connection')
        self.sp = serial.Serial(port=port, baudrate=baud, timeout=2)
        self.sp.flushInput()
        self.sp.flushOutput()
        time.sleep(3)
        print('TCLab connected via Arduino on port ' + port)
        self.start()
        
    def findPort(self):
        found = False
        for port in list(list_ports.comports()):
            # Arduino Uno
            if port[2].startswith('USB VID:PID=16D0:0613'):
                port = port[0]
                found = True
            # HDuino
            if port[2].startswith('USB VID:PID=1A86:7523'):
                port = port[0]
                found = True                
        if (not found):
            print('Arduino COM port not found')
            print('Please ensure that the USB cable is connected')
            print('--- Printing Serial Ports ---')            
            for port in list(serial.tools.list_ports.comports()):
                print(port[0] + ' ' + port[1] + ' ' + port[2])
            port = 'COM3'
        return port