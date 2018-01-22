#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import serial
from serial.tools import list_ports


sep = ' '   # Separates command and value in TCLab firmware

def clip(val, lower=0, upper=100):
    """Limit value to be between lower and upper limits"""
    return max(lower, min(val, upper))


class TCLab(object):
    def __init__(self, port=None, baud=9600, debug=False):
        self.debug = debug
        print('Connecting to TCLab')
        if not port:
            for comport in list(list_ports.comports()):
                if comport[2].startswith('USB VID:PID=16D0:0613'):
                    self.arduino = 'Arduino Uno'
                    break
                elif comport[2].startswith('USB VID:PID=1A86:7523'):
                    self.arduino = 'Hduino'
                    break
                elif comport[2].startswith('USB VID:PID=2341:8036'):
                    self.arduino = 'Arduino Leonardo'
                    break
            else:
                print('--- Printing Serial Ports ---')
                for port in list(list_ports.comports()):
                    print(port[0] + ' ' + port[1] + ' ' + port[2])
                raise RuntimeError('No compatible Arduino device was found.')
            port = comport[0]
        self.sp = serial.Serial(port=port, baudrate=baud, timeout=2)
        self.receive()
        self.version = self.send_and_receive('VER')
        self._P1 = 200.0
        self._P2 = 100.0
        self.Q1(0)
        self.Q2(0)
        if self.sp.isOpen():
            print(self.version + ' on ' + self.arduino + ' connected on port ' + port)
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
        self.send_and_receive('X')
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

    def send_and_receive(self, msg, convert=str):
        """Send a string message and return the response"""
        self.send(msg)
        return convert(self.receive())

    def LED(self, val=100):
        """Flash TCLab LED at a specified brightness (default 100) for 10 seconds."""
        return self.send_and_receive('LED' + sep + str(clip(val)), float)

    @property
    def T1(self):
        """Return a float denoting TCLab temperature T1 in degrees C."""
        return self.send_and_receive('T1', float)

    @property
    def T2(self):
        """Return a float denoting TCLab temperature T2 in degrees C."""
        return self.send_and_receive('T2', float)
    
    @property
    def P1(self):
        """Return a float denoting maximum power of heater 1 in pwm."""
        return self._P1
    
    @P1.setter
    def P1(self, val):
        """Set maximum power of heater 1 in pwm, range 0 to 255."""
        self._P1 = self.send_and_receive('P1' + sep + str(clip(val,0,255)), float)

    @property
    def P2(self):
        """Return a float denoting maximum power of heater 2 in pwm."""
        return self._P2

    @P2.setter
    def P2(self, val):
        """Set maximum power of heater 2 in pwm, range 0 to 255."""
        self._P2 = self.send_and_receive('P2' + sep + str(clip(val,0,255)), float)

    def Q1(self, val=None):
        """Set TCLab heater power Q1 with range limited to 0-100, return clipped value."""
        if val is None:
            msg = 'R1'
        else:
            msg = 'Q1' + sep + str(clip(val))
        return self.send_and_receive(msg, float)

    def Q2(self, val=None):
        """Set TCLab heater power Q1 with range limited to 0-100, return clipped value."""
        if val is None:
            msg = 'R2'
        else:
            msg = 'Q2' + sep + str(clip(val))
        return self.send_and_receive(msg, float)


class TCLabSurrogate(object):
    def __init__(self, port=None, baud=9600, debug=False):
        self.debug = debug
        print('Simulated TCLab')
        self.Ta = 21                  # ambient temperature
        self.tstart = time.time()     # start time
        self.tlast = self.tstart      # last update time
        self._P1 = 200.0              # max power heater 1
        self._P2 = 100.0              # max power heater 2
        self._Q1 = 0                  # initial heater 1
        self._Q2 = 0                  # initial heater 2
        self._T1 = self.Ta            # temperature thermister 1
        self._T2 = self.Ta            # temperature thermister 2
        self._H1 = self.Ta            # temperature heater 1
        self._H2 = self.Ta            # temperature heater 2
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
        """Simulate shutting down TCLab device."""
        self.Q1(0)
        self.Q2(0)
        print('Surrogate TCLab disconnected successfully.')
        return

    def LED(self, val=100):
        self.update()
        """Simulate flashing TCLab LED at a specified brightness (default 100) for 10 seconds."""
        return clip(val)

    @property
    def T1(self):
        self.update()
        """Return a float denoting TCLab temperature T1 in degrees C."""
        return self._T1

    @property
    def T2(self):
        self.update()
        """Return a float denoting TCLab temperature T2 in degrees C."""
        return self._T2

    @property
    def P1(self):
        self.update()
        """Return a float denoting maximum power of heater 1 in pwm."""
        return self._P1
    
    @P1.setter
    def P1(self, val):
        self.update()
        """Set maximum power of heater 1 in pwm, range 0 to 255."""
        self._P1 = clip(val,0,255)

    @property
    def P2(self):
        self.update()
        """Return a float denoting maximum power of heater 2 in pwm."""
        return self._P2

    @P2.setter
    def P2(self, val):
        self.update()
        """Set maximum power of heater 2 in pwm, range 0 to 255."""
        self._P2 = clip(val,0,255)

    def Q1(self, val=None):
        self.update()
        """Simulate setting TCLab heater power Q1 with range limited to 0-100, return clipped value."""
        if val is not None:
            self._Q1 = clip(val)
        return self._Q1

    def Q2(self, val=None):
        self.update()
        """Simulate setting TCLab heater power Q2 with range limited to 0-100, return clipped value."""
        if val is not None:
            self._Q2 = clip(val)
        return self._Q2

    def update(self):
        # Time updates
        self.tnow = time.time()           # current wall clock
        dt = self.tnow - self.tlast       # time step
        self.tlast = self.tnow            # retain for next access

        dH1 = self._P1*self._Q1/5720 \
              + (self.Ta - self._H1)/20 \
              + (self._H2 - self._H1)/100
        dH2 = self._P2*self._Q2/5720 \
              + (self.Ta - self._H2)/20 \
              + (self._H1 - self._H2)/100
        dT1 = (self._H1 - self._T1)/140
        dT2 = (self._H2 - self._T2)/140

        self._H1 += dt * dH1
        self._H2 += dt * dH2
        self._T1 += dt * dT1
        self._T2 += dt * dT2
