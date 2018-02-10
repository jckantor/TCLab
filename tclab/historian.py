#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from collections import Iterable
from .clock import time
import bisect
import sqlite3


class TagDB:
    """Interface to sqlite database containing tag values"""
    def __init__(self, filename=":memory:"):
        """Create or connect to a database

        :param filename: The filename of the database.
                         By default, values are stored in memory."""
        self.db = sqlite3.connect(filename)
        self.cursor = self.db.cursor()
        creates = ["""CREATE TABLE IF NOT EXISTS tagvalues (
                           session_id REFERENCES session (id), 
                           timeseconds, name, value)""",
                   """CREATE TABLE IF NOT EXISTS sessions (
                           id INTEGER PRIMARY KEY, 
                           starttime)"""]
        for statement in creates:
            self.cursor.execute(statement)
        self.db.commit()
        self.session = None

    def new_session(self):
        self.cursor.execute("""INSERT INTO SESSIONS (starttime) 
                               VALUES (datetime('now'))""")
        self.session = self.cursor.lastrowid
        self.db.commit()

    def get_sessions(self):
        result = self.cursor.execute("SELECT id, starttime FROM sessions")
        return list(result)

    def record(self, timeseconds, name, value):
        if self.session is None:
            self.new_session()
        self.cursor.execute("INSERT INTO tagvalues VALUES (?, ?, ?, ?)",
                            (self.session, timeseconds, name, value))
        self.db.commit()

    def get(self, name, timeseconds=None, session=None):
        if session is None:
            session = self.session
        query = """SELECT timeseconds, value FROM tagvalues 
                   WHERE session_id=? AND name=?"""
        parameters = [session, name]
        if timeseconds is not None:
            query += " and timeseconds=?"
            parameters.append(timeseconds)
        query += " ORDER BY timeseconds"
        return list(self.cursor.execute(query, parameters))

    def close(self):
        self.db.close()


class Historian(object):
    """Generalised logging class"""
    def __init__(self, sources, dbfile=":memory:"):
        """
        sources: an iterable of (name, callable) tuples
            - name (str) is the name of a signal and the
            - callable is evaluated to obtain the value.

        Example:

        >>> a = 1
        >>> def getvalue():
        ...     return a
        >>> h = Historian([('a', getvalue)])
        >>> h.update(0)
        >>> h.log
        [(0, 1)]


        Sometimes, multiple values are obtained from one function call. In such
        cases, names can still be specified as before, but callable can be passed
        as None for the subsequent names which come from a previous callable.

        Example:

        >>> a = 1
        >>> b = 2
        >>> def getvalues():
        ...     return [a, b]
        >>> h = Historian([('a', getvalues),
        ...                ('b', None)])
        >>> h.update(0)
        [(0, 1, 2)]

        """
        self.sources = [('Time', lambda: self.tnow)] + list(sources)
        if dbfile:
            self.db = TagDB(dbfile)
            self.db.new_session()
            self.session = self.db.session
        else:
            self.db = None
            self.session = 1

        self.tstart = time()

        self.columns = [name for name, _ in self.sources]

        self.build_fields()

    def build_fields(self):
        self.fields = [[] for _ in self.columns]
        self.logdict = dict(zip(self.columns, self.fields))
        self.t = self.logdict['Time']

    def update(self, tnow=None):
        if tnow is None:
            self.tnow = time() - self.tstart
        else:
            self.tnow = tnow

        for name, valuefunction in self.sources:
            if valuefunction:
                v = valuefunction()
                if isinstance(v, Iterable):
                    values = iter(v)
                else:
                    values = iter([v])
            try:
                value = next(values)
            except StopIteration:
                raise ValueError("valuefunction did not return enough values")

            self.logdict[name].append(value)
            if self.db and name != "Time":
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

    def new_session(self):
        if self.db is None:
            raise NotImplemented("Sessions not supported without dbfile")
        self.db.new_session()
        self.session = self.db.session
        self.tstart = time()
        self.build_fields()

    def get_sessions(self):
        if self.db is None:
            raise NotImplemented("Sessions not supported without dbfile")
        return self.db.get_sessions()

    def load_session(self, session):
        if self.db is None:
            raise NotImplemented("Sessions not supported without dbfile")
        self.db.session = session
        self.build_fields()
        # FIXME: The way time is handled here is a bit brittle
        first = True
        for name in self.columns[1:]:
            for t, value in self.db.get(name):
                self.logdict[name].append(value)
                if first:
                    self.t.append(t)
            first = False

    def close(self):
        if self.db:
            self.db.close()


class Plotter:
    def __init__(self, historian, twindow=120, layout=None):
        """Generalised graphical output of a Historian

        :param historian: An instance of the Historian class
        :param twindow: Amount of time to show in the plot
        :param layout: A tuple of tuples indicating how the fields should be
                plotted. For example (("T1", "T2"), ("Q1", "Q2")) indicates that
                there will be two subplots with the two indicated fields plotted
                on each.
        """
        import matplotlib.pyplot as plt
        from matplotlib import get_backend
        self.backend = get_backend()
        self.historian = historian
        self.twindow = twindow

        if layout is None:
            layout = tuple((field,) for field in historian.columns[1:])
        self.layout = layout

        line_options = {'where': 'post', 'lw': 2, 'alpha': 0.8}
        self.lines = {}
        self.fig, self.axes = plt.subplots(len(layout), 1, figsize=(8, 6),
                                           gridspec_kw={'hspace': 0})
        values = {c: 0 for c in historian.columns}
        plt.setp([a.get_xticklabels() for a in self.axes[:-1]], visible=False)
        for axis, fields in zip(self.axes, self.layout):
            for field in fields:
                y = values[field]
                self.lines[field] = axis.step(0, y, label=field,
                                              **line_options)[0]
            axis.set_xlim(0, self.twindow)
            axis.autoscale(axis='y', tight=False)
            axis.set_ylabel(', '.join(fields))
            if len(fields) > 1:
                axis.legend()
            axis.grid()

        self.axes[-1].set_xlabel('Time / Seconds')
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
            for axis in self.axes:
                axis.set_xlim(tmin, tmax)
        t = self.historian.fields[0]
        for axis, fields in zip(self.axes, self.layout):
            for field in fields:
                y = self.historian.logdict[field]
                self.lines[field].set_data(t, y)
            axis.relim()
            axis.autoscale_view()
        self.fig.canvas.draw()
        if self.backend != 'nbAgg':
            self.display.clear_output(wait=True)
            self.display.display(self.fig)
