#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
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
        self.sources = [('T1', lambda: self.T1),
                        ('T2', lambda: self.T2),
                        ('Q1', self.Q1),
                        ('Q2', self.Q2),
                        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return

    def close(self):
        """Shut down TCLab device and close serial connection."""
        self.Q1(0)
        self.Q2(0)
        self.send('X')
        self.receive()
        self.sp.close()
        print('TCLab disconnected successfully.')
        return

    def send(self, msg):
        """Send a string message to the TCLab firmware."""
        self.sp.write((msg + '\r\n').encode())
        if self.debug:
            print('Sent: "' + msg + '"')
        self.sp.flush()

    def receive(self):
        """Return a string message received from the TCLab firmware."""
        msg = self.sp.readline().decode('UTF-8').replace('\r\n', '')
        if self.debug:
            print('Return: "' + msg + '"')
        return msg
    
    def LED(self, val=100):
        """Flash TCLab LED at a specified brightness (default 100) for 10 seconds."""
        val = max(0, min(val, 100))
        self.send('LED ' + str(val))
        return float(self.receive())

    @property
    def T1(self):
        """Return a float denoting TCLab temperature T1 in degrees C."""
        self.send('T1')
        self._T1 = float(self.receive())
        return self._T1

    @property
    def T2(self):
        """Return a float denoting TCLab temperature T2 in degrees C."""
        self.send('T2')
        self._T2 = float(self.receive())
        return self._T2

    def Q1(self, val=None):
        """Set TCLab heater power Q1 with range limited to 0-100, and actual value."""
        if val is None:
            self.send('R1')
        else:
            val = max(0, min(val, 100))
            self.send('Q1 ' + str(val))
        self._Q1 = float(self.receive())
        return self._Q1

    def Q2(self, val=None):
        """Set TCLab heater power Q1 with range limited to 0-100, and actual value."""
        if val is None:
            self.send('R2')
        else:
            val = max(0, min(val, 100))
            self.send('Q2 ' + str(val))
        self._Q2 = float(self.receive())
        return self._Q2
