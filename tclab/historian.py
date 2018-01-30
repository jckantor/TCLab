#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from .clock import time
import bisect
import sqlite3

class TagDB:
    """Interface to sqlite database containing tag values"""
    def __init__(self, filename=":memory:"):
        self.db = sqlite3.connect(filename)
        self.db.execute("CREATE TABLE IF NOT EXISTS tagvalues (timestamp, name, value)")
        self.db.commit()

    def record(self, timestamp, name, value):
        self.db.execute("INSERT INTO tagvalues VALUES (?, ?, ?)",
                        (timestamp, name, value))
        self.db.commit()


class Historian(object):
    """Generalised logging class"""
    def __init__(self, sources, dbfile=":memory:"):
        """

        sources: an iterable of (name, callable) tuples
                     - name (str) is the name of a signal and the
                     - callable is evaluated to obtain the value
        """
        self.sources = [('Time', lambda: self.tnow)] + list(sources)
        self.db = TagDB(dbfile)
        self.tstart = time()
        self.tnow = 0
        self.columns = [name for name, _ in self.sources]
        self.fields = [[] for _ in range(len(self.sources))]
        self.logdict = {c: f for c, f in zip(self.columns, self.fields)}
        self.t = self.logdict['Time']

        self.update(tnow=0)

    def update(self, tnow=None):
        if tnow is None:
            self.tnow = time()
        else:
            self.tnow = tnow

        for name, valuefunction in self.sources:
            value = valuefunction()
            self.logdict[name].append(value)
            if name != "Time":
                self.db.record(self.tnow, name, value)

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
    def __init__(self, historian, twindow=120):
        import matplotlib.pyplot as plt
        from matplotlib import get_backend
        self.backend = get_backend()
        self.historian = historian
        self.twindow = twindow
        self.nplots = len(self.historian.columns) - 1
        line_options = {'where': 'post', 'lw': 2, 'alpha': 0.8}
        self.lines = []
        self.fig, self.axes = plt.subplots(self.nplots, 1, figsize=(8,6))
        for n in range(0, self.nplots):
            y = self.historian.at(0,[self.historian.columns[n+1]])[0]
            self.lines.append(self.axes[n].step(0, y, **line_options)[0])
            self.axes[n].set_xlim(0, self.twindow)
            self.axes[n].set_ylim(y-2, y+2)
            self.axes[n].set_ylabel(self.historian.columns[n+1])
            self.axes[n].grid()
        self.axes[self.nplots-1].set_xlabel('Time / Seconds')
        plt.tight_layout()
        self.fig.canvas.draw()
        self.fig.show()
        if self.backend != 'nbAgg':
            from IPython import display
            self.display = display
            self.display.clear_output(wait=True)
            self.display.display(self.fig)

    def update(self, tnow=None):
        self.historian.update(tnow)
        if self.historian.tnow > self.twindow:
            tmin = self.historian.tnow - self.twindow
            tmax = self.historian.tnow
            for n in range(0, self.nplots):
                self.axes[n].set_xlim(tmin, tmax)
        t = self.historian.fields[0]
        for n in range(0, self.nplots):
            y = self.historian.fields[n+1]
            self.lines[n].set_data(t, y)
            ymin, ymax = self.axes[n].get_ylim()
            if max(y) > ymax - 0.05*(ymax - ymin):
                ymax = max(y) + 0.10*(ymax - ymin)
                self.axes[n].set_ylim(ymin, ymax)
            if min(y) < ymin + 0.05*(ymax - ymin):
                ymin = min(y) - 0.10*(ymax - ymin)
                self.axes[n].set_ylim(ymin, ymax)
        self.fig.canvas.draw()
        if self.backend != 'nbAgg':
            self.display.clear_output(wait=True)
            self.display.display(self.fig)

