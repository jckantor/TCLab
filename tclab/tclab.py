#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import serial
from serial.tools import list_ports

class TCLab(object):

    def __init__(self, port=None, baud=9600, debug=False):
        self.debug = debug
        print('Connecting to TCLab')
        if not port:
            for comport in list(list_ports.comports()):
                if comport[2].startswith((
                        'USB VID:PID=16D0:0613',    # Arduino Uno
                        'USB VID:PID=1A86:7523',    # Hduino
                        'USB VID:PID=2341:8036')):  # Arduino Leonardo
                    break
            else:
                print('--- Printing Serial Ports ---')
                for port in list(list_ports.comports()):
                    print(port[0] + ' ' + port[1] + ' ' + port[2])
                raise RuntimeError('No Arduino device was found.')
            port = comport[0]
        self.sp = serial.Serial(port=port, baudrate=baud, timeout=2)
        self.receive()
        self.send('VER')
        self.version = self.receive()
        self.Q1(0)
        self.Q2(0)
        if self.sp.isOpen():
            print(self.version + ' connected on port ' + port)
        self.tstart = time.time()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return

    def close(self):
        try:
            self.Q1(0)
            self.Q2(0)
            self.send('X')
            self.receive()
            self.sp.close()
            print('TCLab disconnected successfully.')
        except:
            print('Problem encountered while disconnecting from TCLab.')
            print('Please unplug and replug tclab.')
        return

    def send(self,msg):
        self.sp.write((msg + '\r\n').encode())
        if self.debug:
            print('Sent: "' + msg + '"')
        self.sp.flush()

    def receive(self):
        msg = self.sp.readline().decode('UTF-8').replace('\r\n','')
        if self.debug:
            print('Return: "' + msg + '"')
        return msg
    
    def LED(self,val=100):
        val = max(0, min(val, 100))
        self.send('LED ' + str(val))
        return float(self.receive())

    @property
    def T1(self):
        self.send('T1')
        self._T1 = float(self.receive())
        return self._T1

    @property
    def T2(self):
        self.send('T2')
        self._T2 = float(self.receive())
        return self._T2

    def Q1(self,val=None):
        if val is None:
            self.send('R1')
            self._Q1 = float(self.receive())
        else:
            val = max(0, min(val, 100))
            self.send('Q1 ' + str(val))
            self._Q1 = float(self.receive())
        return self._Q1

    def Q2(self,val=None):
        if val is None:
            self.send('R2')
            self._Q2 = float(self.receive())
        else:
            val = max(0, min(val, 100))
            self.send('Q2 ' + str(val))
            self._Q2 = float(self.receive())
        return self._Q2
