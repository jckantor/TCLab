#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:14:07 2018

@author: jeff
"""
from __future__ import print_function
from __future__ import division

import time
import matplotlib.pyplot as plt
from IPython import display


class Historian(object):
    def __init__(self, lab):
        self.lab = lab
        self.tstart = time.time()
        self.RTplot = False
        self.t = []
        self.T1 = []
        self.T2 = []
        self.Q1 = []
        self.Q2 = []
        self.columns = ['Time', 'T1', 'T2', 'Q1', 'Q2']
        self.fields = [self.t, self.T1, self.T2, self.Q1, self.Q2]
        self.logdict = {c: f for c, f in zip(self.columns, self.fields)}

        self.update(tnow=0)

    def initplot(self, tperiod=20):
        self.RTplot = True
        self.tnow = 0
        T1 = self.T1[0]
        T2 = self.T2[0]
        plt.figure(figsize=(10, 5))
        self.ax1 = plt.subplot(2, 1, 1)
        self.line_T1, = plt.plot(0, T1, lw=2, alpha=0.8)
        self.line_T2, = plt.plot(0, T2, lw=2, alpha=0.8)
        plt.xlim(0, 1.05*tperiod)
        Tmax = max(T1, T2)
        Tmin = min(T1, T2)
        self.ax1.set_ylim(Tmin - (Tmin%5), Tmax + 5 - (Tmax%5))        
        plt.title('Temperature Control Lab')
        plt.ylabel(u'Temperature / °C')
        plt.xlabel('Time / Seconds')
        plt.legend(['T1', 'T2'])
        plt.grid()

        self.ax2 = plt.subplot(2, 1, 2)
        self.line_Q1, = plt.step(0, self.Q1[0], where='pre', lw=2, alpha=0.8)
        self.line_Q2, = plt.step(0, self.Q2[0], where='pre', lw=2, alpha=0.8)
        plt.xlim(0, 1.05*tperiod)
        plt.ylim(-5, 110)
        plt.ylabel('Percent of Max Power')
        plt.xlabel('Time / Seconds')
        plt.legend(['Q1','Q2'])
        plt.grid()
        plt.tight_layout()
        
    def update(self, tnow=None):
        if tnow is None:
            self.tnow = time.time() - self.tstart
        else:
            self.tnow = tnow
        row = [self.tnow, self.lab.T1, self.lab.T2, self.lab.Q1(), self.lab.Q2()]
        for c, v in zip(self.columns, row):
            self.logdict[c].append(v)
        if self.RTplot:
            self.updateplot()

    def updateplot(self):
        [t, T1, T2, Q1, Q2] = [self.logdict[c] for c in self.columns]
        self.line_T1.set_xdata(t)
        self.line_T1.set_ydata(T1)
        self.line_T2.set_xdata(t)
        self.line_T2.set_ydata(T2)
        self.line_Q1.set_xdata(t)
        self.line_Q1.set_ydata(Q1)
        self.line_Q2.set_xdata(t)
        self.line_Q2.set_ydata(Q2)
        if self.tnow > self.ax1.get_xlim()[1]:
            self.ax1.set_xlim(0, 1.4*self.ax1.get_xlim()[1])
            self.ax2.set_xlim(0, 1.4*self.ax2.get_xlim()[1])
        Tmax = max(max(T1), max(T2))
        Tmin = min(min(T1), min(T2))
        if (Tmax > self.ax1.get_ylim()[1]) or (Tmin < self.ax1.get_ylim()[0]):
            self.ax1.set_ylim(Tmin - (Tmin%5), Tmax + 5 - (Tmax%5))
        display.clear_output(wait=True)
        display.display(plt.gcf())

    @property
    def log(self):
        return list(zip(*[self.logdict[c] for c in self.columns]))

