#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:14:07 2018

@author: jeff
"""

import time
from math import ceil, floor
import numpy as np
import matplotlib.pyplot as plt
from IPython import display
import pandas as pd

class Historian(object):
    
    def __init__(self,lab):
        self._log = []
        self.lab = lab
        self.tstart = time.time()
        self.RTplot = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        return
    
    def update(self):
        self.tp = time.time() - self.tstart
        self.T1 = self.lab.T1
        self.T2 = self.lab.T2
        self.Q1 = self.lab.Q1()
        self.Q2 = self.lab.Q2()

        self._log.append([self.tp, self.T1, self.T2, self.Q1, self.Q2])
        if self.RTplot:
            self.updateplot()

    def initplot(self, tf=20):
        self.RTplot = True
        # create an empty plot, and keep the line object around
        plt.figure(figsize=(12, 6))
        self.ax1 = plt.subplot(2, 1, 1)
        self.line_T1, = plt.plot(0, self.lab.T1, lw=2, alpha=0.8)
        self.line_T2, = plt.plot(0, self.lab.T2, lw=2, alpha=0.8)
        plt.xlim(0, 1.05*tf)
        plt.title('Temperature Control Lab')
        plt.ylabel('Temperature / °C')
        plt.xlabel('Time / Seconds')
        plt.legend(['T1', 'T2'])
        plt.grid()

        self.ax2 = plt.subplot(2,1,2)
        self.line_Q1, = plt.step(0, self.lab.Q1(), where='post', lw=2, alpha=0.8)
        self.line_Q2, = plt.step(0, self.lab.Q2(), where='post', lw=2, alpha=0.8)
        plt.xlim(0, 1.05*tf)
        plt.ylim(-5, 110)
        plt.ylabel('Percent of Maximum Power')
        plt.xlabel('Time / Seconds')
        plt.legend(['Q1','Q2'])
        plt.grid()
        plt.tight_layout()

    def updateplot(self):
        self.line_T1.set_xdata(np.append(self.line_T1.get_xdata(), self.tp))
        self.line_T1.set_ydata(np.append(self.line_T1.get_ydata(), self.T1))
        self.line_T2.set_xdata(np.append(self.line_T2.get_xdata(), self.tp))
        self.line_T2.set_ydata(np.append(self.line_T2.get_ydata(), self.T2))
        self.line_Q1.set_xdata(np.append(self.line_Q1.get_xdata(), self.tp))
        self.line_Q1.set_ydata(np.append(self.line_Q1.get_ydata(), self.Q1))
        self.line_Q2.set_xdata(np.append(self.line_Q2.get_xdata(), self.tp))
        self.line_Q2.set_ydata(np.append(self.line_Q2.get_ydata(), self.Q2))
        if self.tp > self.ax1.get_xlim()[1]:
            self.ax1.set_xlim(0, 1.5*self.ax1.get_xlim()[1])
            self.ax2.set_xlim(0, 1.5*self.ax2.get_xlim()[1])
        Tmax = max(max(self.line_T1.get_ydata()), max(self.line_T2.get_ydata()))
        Tmin = min(min(self.line_T1.get_ydata()), min(self.line_T2.get_ydata()))
        if (Tmax > self.ax1.get_ylim()[1]) or (Tmin < self.ax1.get_ylim()[0]):
            self.ax1.set_ylim(5*floor(Tmin/5), 5*ceil(Tmax/5))
        display.clear_output(wait=True)
        display.display(plt.gcf())

    @property
    def log(self):
        df = pd.DataFrame(self._log, columns = ['Time','Q1','Q2','T1','T2'])
        df.set_index('Time',inplace=True)
        return df

