#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import serial
from serial.tools import list_ports

from math import ceil, floor
import numpy as np
import matplotlib.pyplot as plt
from IPython import display

class TCLab(object):

    def __init__(self, port=None, baud=9600, debug=False):
        self.debug = debug
        self._Q1 = 0
        self._Q2 = 0
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
        if self.sp.isOpen():
            print('TCLab connected on port ' + port)
        self.tstart = time.time()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return

    def close(self):
        try:
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

    def initplot(self,tf=20):
        # create an empty plot, and keep the line object around
        plt.figure(figsize=(12,6))
        self.ax1 = plt.subplot(2,1,1)
        self.line_T1, = plt.plot(0,self.T1,lw=2,alpha=0.8)
        self.line_T2, = plt.plot(0,self.T2,lw=2,alpha=0.8)
        plt.xlim(0,1.05*tf)
        plt.title('Temperature Control Lab')
        plt.ylabel('Temperature / °C')
        plt.xlabel('Time / Seconds')
        plt.legend(['T1','T2'])
        plt.grid()

        self.ax2 = plt.subplot(2,1,2)
        self.line_Q1, = plt.step(0,self.Q1(),where='post',lw=2,alpha=0.8)
        self.line_Q2, = plt.step(0,self.Q2(),where='post',lw=2,alpha=0.8)
        plt.xlim(0,1.05*tf)
        plt.ylim(-5,110)
        plt.ylabel('Percent of Maximum Power')
        plt.xlabel('Time / Seconds')
        plt.legend(['Q1','Q2'])
        plt.grid()
        plt.tight_layout()

    def updateplot(self):
        tp = time.time() - self.tstart
        T1,T2,Q1,Q2 = self.T1,self.T2,self.Q1(),self.Q2()
        self.line_T1.set_xdata(np.append(self.line_T1.get_xdata(),tp))
        self.line_T1.set_ydata(np.append(self.line_T1.get_ydata(),T1))
        self.line_T2.set_xdata(np.append(self.line_T2.get_xdata(),tp))
        self.line_T2.set_ydata(np.append(self.line_T2.get_ydata(),T2))
        self.line_Q1.set_xdata(np.append(self.line_Q1.get_xdata(),tp))
        self.line_Q1.set_ydata(np.append(self.line_Q1.get_ydata(),Q1))
        self.line_Q2.set_xdata(np.append(self.line_Q2.get_xdata(),tp))
        self.line_Q2.set_ydata(np.append(self.line_Q2.get_ydata(),Q2))
        if tp > self.ax1.get_xlim()[1]:
            self.ax1.set_xlim(0,1.5*self.ax1.get_xlim()[1])
            self.ax2.set_xlim(0,1.5*self.ax2.get_xlim()[1])
        Tmax = max(max(self.line_T1.get_ydata()),max(self.line_T2.get_ydata()))
        Tmin = min(min(self.line_T1.get_ydata()),min(self.line_T2.get_ydata()))
        if (Tmax > self.ax1.get_ylim()[1]) or (Tmin < self.ax1.get_ylim()[0]):
            self.ax1.set_ylim(5*floor(Tmin/5), 5*ceil(Tmax/5))
        display.clear_output(wait=True)
        display.display(plt.gcf())
