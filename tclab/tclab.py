#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import os
import random
import serial
from serial.tools import list_ports
from .labtime import labtime
from .version import __version__


sep = ' '   # command/value separator in TCLab firmware

arduinos = [('USB VID:PID=16D0:0613', 'Arduino Uno'),
            ('USB VID:PID=1A86:7523', 'NHduino'),
            ('USB VID:PID=2341:8036', 'Arduino Leonardo'),
            ('USB VID:PID=2A03', 'Arduino.org device'),
            ('USB VID:PID', 'unknown device'),
            ]

_sketchurl = 'https://github.com/jckantor/TCLab-sketch'
_connected = False


def clip(val, lower=0, upper=100):
    """Limit value to be between lower and upper limits"""
    return max(lower, min(val, upper))


def command(name, argument, lower=0, upper=100):
    """Construct command to TCLab-sketch."""
    return name + sep + str(clip(argument, lower, upper))


def find_arduino(port=''):
    """Locates Arduino and returns port and device."""
    comports = [tuple for tuple in list_ports.comports() if port in tuple[0]]
    for port, desc, hwid in comports:
        for identifier, arduino in arduinos:
            if hwid.startswith(identifier):
                return port, arduino
    print('--- Serial Ports ---')
    for port, desc, hwid in list_ports.comports():
        print(port, desc, hwid)
    return None, None


class AlreadyConnectedError(Exception):
    pass


class TCLab(object):
    def __init__(self, port='', debug=False):
        global _connected
        self.debug = debug
        print("TCLab version", __version__)
        self.port, self.arduino = find_arduino(port)
        if self.port is None:
            raise RuntimeError('No Arduino device found.')

        try:
            self.connect(baud=115200)
        except AlreadyConnectedError:
            raise
        except:
            try:
                _connected = False
                self.sp.close()
                self.connect(baud=9600)
                print('Could not connect at high speed, but succeeded at low speed.')
                print('This may be due to an old TCLab firmware.')
                print('New Arduino TCLab firmware available at:')
                print(_sketchurl)
            except:
                raise RuntimeError('Failed to Connect.')

        self.sp.readline().decode('UTF-8')
        self.version = self.send_and_receive('VER')
        if self.sp.isOpen():
            print(self.arduino, 'connected on port', self.port,
                  'at', self.baud, 'baud.')
            print(self.version + '.')
        labtime.set_rate(1)
        labtime.start()
        self._P1 = 200.0
        self._P2 = 100.0
        self.Q2(0)
        self.sources = [('T1', self.scan),
                        ('T2', None),
                        ('Q1', None),
                        ('Q2', None),
                        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return

    def connect(self, baud):
        """Establish a connection to the arduino

        baud: baud rate"""
        global _connected

        if _connected:
            raise AlreadyConnectedError('You already have an open connection')

        _connected = True

        self.sp = serial.Serial(port=self.port, baudrate=baud, timeout=2)
        time.sleep(2)
        self.Q1(0)  # fails if not connected
        self.baud = baud

    def close(self):
        """Shut down TCLab device and close serial connection."""
        global _connected

        self.Q1(0)
        self.Q2(0)
        self.send_and_receive('X')
        self.sp.close()
        _connected = False
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
        """Flash TCLab LED at a specified brightness for 10 seconds."""
        return self.send_and_receive(command('LED', val), float)

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
        self._P1 = self.send_and_receive(command('P1', val, 0, 255), float)

    @property
    def P2(self):
        """Return a float denoting maximum power of heater 2 in pwm."""
        return self._P2

    @P2.setter
    def P2(self, val):
        """Set maximum power of heater 2 in pwm, range 0 to 255."""
        self._P2 = self.send_and_receive(command('P2', val, 0, 255), float)

    def Q1(self, val=None):
        """Get or set TCLab heater power Q1

        val: Value of heater power, range is limited to 0-100

        return clipped value."""
        if val is None:
            msg = 'R1'
        else:
            msg = 'Q1' + sep + str(clip(val))
        return self.send_and_receive(msg, float)

    def Q2(self, val=None):
        """Get or set TCLab heater power Q2

        val: Value of heater power, range is limited to 0-100

        return clipped value."""
        if val is None:
            msg = 'R2'
        else:
            msg = 'Q2' + sep + str(clip(val))
        return self.send_and_receive(msg, float)

    def scan(self):
        #self.send('SCAN')
        T1 = self.T1  # float(self.receive())
        T2 = self.T2  # float(self.receive())
        Q1 = self.Q1()  # float(self.receive())
        Q2 = self.Q2()  # float(self.receive())
        return T1, T2, Q1, Q2

    # Define properties for Q1 and Q2
    U1 = property(fget=Q1, fset=Q1, doc="Heater 1 value")
    U2 = property(fget=Q2, fset=Q2, doc="Heater 2 value")


class TCLabModel(object):
    def __init__(self, port='', debug=False, synced=True):
        self.debug = debug
        self.synced = synced
        print("TCLab version", __version__)
        labtime.start()
        print('Simulated TCLab')
        self.Ta = 21                  # ambient temperature
        self.tstart = labtime.time()  # start time
        self.tlast = self.tstart      # last update time
        self._P1 = 200.0              # max power heater 1
        self._P2 = 100.0              # max power heater 2
        self._Q1 = 0                  # initial heater 1
        self._Q2 = 0                  # initial heater 2
        self._T1 = self.Ta            # temperature thermister 1
        self._T2 = self.Ta            # temperature thermister 2
        self._H1 = self.Ta            # temperature heater 1
        self._H2 = self.Ta            # temperature heater 2
        self.maxstep = 0.2            # maximum time step for integration
        self.sources = [('T1', self.scan),
                        ('T2', None),
                        ('Q1', None),
                        ('Q2', None),
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
        print('TCLab Model disconnected successfully.')
        return

    def LED(self, val=100):
        """Simulate flashing TCLab LED

           val : specified brightness (default 100). """
        self.update()
        return clip(val)

    @property
    def T1(self):
        """Return a float denoting TCLab temperature T1 in degrees C."""
        self.update()
        return self.measurement(self._T1)

    @property
    def T2(self):
        """Return a float denoting TCLab temperature T2 in degrees C."""
        self.update()
        return self.measurement(self._T2)

    @property
    def P1(self):
        """Return a float denoting maximum power of heater 1 in pwm."""
        self.update()
        return self._P1

    @P1.setter
    def P1(self, val):
        """Set maximum power of heater 1 in pwm, range 0 to 255."""
        self.update()
        self._P1 = clip(val, 0, 255)

    @property
    def P2(self):
        """Return a float denoting maximum power of heater 2 in pwm."""
        self.update()
        return self._P2

    @P2.setter
    def P2(self, val):
        """Set maximum power of heater 2 in pwm, range 0 to 255."""
        self.update()
        self._P2 = clip(val, 0, 255)

    def Q1(self, val=None):
        """Get or set TCLabModel heater power Q1

        val: Value of heater power, range is limited to 0-100

        return clipped value."""
        self.update()
        if val is not None:
            self._Q1 = clip(val)
        return self._Q1

    def Q2(self, val=None):
        """Get or set TCLabModel heater power Q2

        val: Value of heater power, range is limited to 0-100

        return clipped value."""
        self.update()
        if val is not None:
            self._Q2 = clip(val)
        return self._Q2

    def scan(self):
        self.update()
        return (self.measurement(self._T1),
                self.measurement(self._T2),
                self._Q1,
                self._Q2)

    # Define properties for Q1 and Q2
    U1 = property(fget=Q1, fset=Q1, doc="Heater 1 value")
    U2 = property(fget=Q2, fset=Q2, doc="Heater 2 value")

    def quantize(self, T):
        """Quantize model temperatures to mimic Arduino A/D conversion."""
        return max(-50, min(132.2, T - T % 0.3223))

    def measurement(self, T):
        return self.quantize(T + random.normalvariate(0, 0.043))

    def update(self, t=None):
        if t is None:
            if self.synced:
                self.tnow = labtime.time() - self.tstart
            else:
                return
        else:
            self.tnow = t

        teuler = self.tlast

        while teuler < self.tnow:
            dt = min(self.maxstep, self.tnow - teuler)
            DeltaTaH1 = self.Ta - self._H1
            DeltaTaH2 = self.Ta - self._H2
            DeltaT12 = self._H1 - self._H2
            dH1 = self._P1 * self._Q1 / 5720 + DeltaTaH1 / 20 - DeltaT12 / 100
            dH2 = self._P2 * self._Q2 / 5720 + DeltaTaH2 / 20 + DeltaT12 / 100
            dT1 = (self._H1 - self._T1)/140
            dT2 = (self._H2 - self._T2)/140

            self._H1 += dt * dH1
            self._H2 += dt * dH2
            self._T1 += dt * dT1
            self._T2 += dt * dT2
            teuler += dt

        self.tlast = self.tnow


def diagnose(port=''):
    def countdown(t=10):
        for i in reversed(range(t)):
            print('\r' + "Countdown: {0:d}  ".format(i), end='', flush=True)
            time.sleep(1)
        print()

    def heading(string):
        print()
        print(string)
        print('-'*len(string))

    heading('Checking connection')

    if port:
        print('Looking for Arduino on {} ...'.format(port))
    else:
        print('Looking for Arduino on any port...')
    comport, name = find_arduino(port=port)

    if comport is None:
        print('No known Arduino was found in the ports listed above.')
        return

    print(name, 'found on port', comport)

    heading('Testing TCLab object in debug mode')

    with TCLab(port=port, debug=True) as lab:
        print('Reading temperature')
        print(lab.T1)

    heading('Testing TCLab functions')

    with TCLab(port=port) as lab:
        print('Testing LED. Should turn on for 10 seconds.')
        lab.LED(100)
        countdown()

        print()
        print('Reading temperatures')
        T1 = lab.T1
        T2 = lab.T2
        print('T1 = {} °C, T2 = {} °C'.format(T1, T2))

        print()
        print('Writing fractional value to heaters...')
        try:
            Q1 = lab.Q1(0.5)
        except:
            Q1 = -1.0
        print("We wrote Q1 = 0.5, and read back Q1 =", Q1)

        if Q1 != 0.5:
            print("Your TCLab firmware version ({}) doesn't support"
                  "fractional heater values.".format(lab.version))
            print("You need to upgrade to at least version 1.4.0 for this:")
            print(_sketchurl)

        print()
        print('We will now turn on the heaters, wait 30 seconds '
              'and see if the temperatures have gone up. ')
        lab.Q1(100)
        lab.Q2(100)
        countdown(30)

        print()
        def tempcheck(name, T_initial, T_final):
            print('{} started a {} °C and went to {} °C'
                  .format(name, T_initial, T_final))
            if T_final - T_initial < 0.8:
                print('The temperature went up less than expected.')
                print('Check the heater power supply.')

        T1_final = lab.T1
        T2_final = lab.T2

        tempcheck('T1', T1, T1_final)
        tempcheck('T2', T2, T2_final)

        print()
        heading("Throughput check")
        print("This part checks how fast your unit is")
        print("We will read T1 as fast as possible")

        start = time.time()
        n = 0
        while time.time() - start < 10:
            elapsed = time.time() - start + 0.0001  # avoid divide by zero
            T1 = lab.T1
            n += 1
            print('\rTime elapsed: {:3.2f} s.'
                  ' Number of reads: {}.'
                  ' Sampling rate: {:2.2f} Hz'.format(elapsed, n, n/elapsed),
                  end='')

        print()

    print()
    print('Diagnostics complete')
