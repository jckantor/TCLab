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

        self.fig = plt.figure(figsize=(8, 6))
        nplots = len(self.historian.columns) - 1  
        self.lines = []
        self.axes = []
        for n in range(0, nplots):
            self.axes.append(self.fig.add_subplot(nplots,1,n+1))
            y = self.historian.at(0,[self.historian.columns[n+1]])[0]
            li, = plt.step(0, y, where='post', **line_options)          
            self.lines.append(li)
            plt.xlim(0, 1.05 * tperiod)
            plt.ylim(y-2,y+2)
            plt.ylabel(self.historian.columns[n+1])
            plt.grid()
        plt.xlabel('Time / Seconds')
        plt.tight_layout()
        display.display(plt.gcf())

    def update(self, tnow=None):
        self.historian.update(tnow)

        plt = self.plt
        display = self.display

        t = self.historian.fields[0]
        for n in range(0, len(self.historian.columns)-1):
            y = self.historian.fields[n+1]
            self.lines[n].set_data(t,y)
            ymax = max(y)
            ymin = min(y)
            if (ymax > self.axes[n].get_ylim()[1]) or (ymin < self.axes[n].get_ylim()[0]):
                self.axes[n].set_ylim(ymin-1,ymax+2)
            if self.historian.tnow > self.axes[n].get_xlim()[1]:
                self.axes[n].set_xlim(0, 1.4 * self.axes[n].get_xlim()[1])
        display.clear_output(wait=True)
        display.display(plt.gcf())

