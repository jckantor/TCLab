#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

        line_options = {'lw': 2, 'alpha': 0.8}

        plt.figure(figsize=(10, 5))
        self.ax1 = plt.gca()
        val = [self.historian.at(0, [pv]) for pv in self.historian.columns]
        self.lines = []
        for k in range(1,len(self.historian.columns)):
            li, = plt.step(val[0], val[k], where='pre', **line_options)
            self.lines.append(li)
        plt.xlim(0, 1.05 * tperiod)
        plt.ylim(-2, 105)
        plt.title('Temperature Control Lab')
        plt.xlabel('Time / Seconds')
        plt.legend(self.historian.columns[1:])
        plt.grid()

    def update(self, tnow=None):
        self.historian.update(tnow)

        plt = self.plt
        display = self.display

        t = self.historian.fields[0]
        for k in range(1,len(self.historian.columns)):
            self.lines[k-1].set_data(t,self.historian.fields[k])
        if self.historian.tnow > self.ax1.get_xlim()[1]:
            self.ax1.set_xlim(0, 1.4 * self.ax1.get_xlim()[1])
        display.clear_output(wait=True)
        display.display(plt.gcf())

