#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:14:07 2018

@author: jeff
"""
from __future__ import print_function
from __future__ import division
import time
import bisect

class Historian(object):
    """Generalised logging class"""
    def __init__(self, sources):
        """

        sources: an iterable of (name, callable) tuples
                     - name (str) is the name of a signal and the
                     - callable is evaluated to obtain the value
        """
        self.sources = [('Time', lambda: self.tnow)] + list(sources)
        self.tstart = time.time()
        self.tnow = 0
        self.columns = [name for name, _ in self.sources]
        self.fields = [[] for _ in range(len(self.sources))]
        self.logdict = {c: f for c, f in zip(self.columns, self.fields)}
        self.t = self.logdict['Time']

        self.update(tnow=0)

    def update(self, tnow=None):
        if tnow is None:
            self.tnow = time.time() - self.tstart
        else:
            self.tnow = tnow

        for n, c in self.sources:
            self.logdict[n].append(c())

    @property
    def log(self):
        return list(zip(*[self.logdict[c] for c in self.columns]))

    def at(self, t, columns=None):
        """ Return the values of columns at or just before a certain time"""
        if columns is None:
            columns = self.columns
        i = bisect.bisect(self.t, t) - 1
        return [self.logdict[c][i] for c in columns]


class Plotter:
    def __init__(self, historian, tperiod=20):
        self.historian = historian

        import matplotlib.pyplot as plt
        from IPython import display

        self.plt = plt
        self.display = display

        t, T1, T2, Q1, Q2 = self.historian.at(0)

        line_options = {'lw': 2, 'alpha': 0.8}

        plt.figure(figsize=(10, 5))
        self.ax1 = plt.subplot(2, 1, 1)
        self.line_T1, = plt.plot(0, T1, **line_options)
        self.line_T2, = plt.plot(0, T2, **line_options)
        plt.xlim(0, 1.05 * tperiod)
        Tmax = max(T1, T2)
        Tmin = min(T1, T2)
        self.ax1.set_ylim(Tmin - (Tmin % 5), Tmax + 5 - (Tmax % 5))
        plt.title('Temperature Control Lab')
        plt.ylabel(u'Temperature / °C')
        plt.xlabel('Time / Seconds')
        plt.legend(['T1', 'T2'])
        plt.grid()

        self.ax2 = plt.subplot(2, 1, 2)
        self.line_Q1, = plt.step(0, Q1, where='pre', **line_options)
        self.line_Q2, = plt.step(0, Q2, where='pre', **line_options)
        plt.xlim(0, 1.05 * tperiod)
        plt.ylim(-5, 110)
        plt.ylabel('Percent of Max Power')
        plt.xlabel('Time / Seconds')
        plt.legend(['Q1', 'Q2'])
        plt.grid()
        plt.tight_layout()

    def update(self, tnow=None):
        self.historian.update(tnow)

        plt = self.plt
        display = self.display

        t, T1, T2, Q1, Q2 = self.historian.fields
        self.line_T1.set_data(t, T1)
        self.line_T2.set_data(t, T2)
        self.line_Q1.set_data(t, Q1)
        self.line_Q2.set_data(t, Q2)
        if self.historian.tnow > self.ax1.get_xlim()[1]:
            self.ax1.set_xlim(0, 1.4 * self.ax1.get_xlim()[1])
            self.ax2.set_xlim(0, 1.4 * self.ax2.get_xlim()[1])
        Tmax = max(max(T1), max(T2))
        Tmin = min(min(T1), min(T2))
        if (Tmax > self.ax1.get_ylim()[1]) or (
                Tmin < self.ax1.get_ylim()[0]):
            self.ax1.set_ylim(Tmin - (Tmin % 5), Tmax + 5 - (Tmax % 5))
        display.clear_output(wait=True)
        display.display(plt.gcf())
