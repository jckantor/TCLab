#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from collections import Iterable
import bisect
import sqlite3
from .labtime import labtime
import time


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
        query = """SELECT id, starttime, COUNT(DISTINCT timeseconds) 
                   FROM sessions LEFT JOIN tagvalues ON sessions.id=session_id
                   GROUP BY id ORDER BY starttime"""
        return list(self.cursor.execute(query))

    def delete_session(self, session_id):
        queries = ['DELETE FROM sessions WHERE id = ?',
                   'DELETE FROM tagvalues WHERE session_id = ?']
        for query in queries:
            self.cursor.execute(query, (session_id,))
        self.db.commit()

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

    def clean(self):
        """Delete sessions with no associated points"""
        query = """DELETE FROM sessions WHERE id NOT IN 
                   (SELECT DISTINCT session_id FROM tagvalues)"""
        self.cursor.execute(query)
        self.db.commit()

    def close(self):
        self.clean()
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
        cases, names can still be specified as before, but callable can be
        passed as None for the subsequent names which come from a previous
        callable.

        Example:

        >>> a = 1
        >>> b = 2
        >>> def getvalues():
        ...     return [a, b]
        >>> h = Historian([('a', getvalues),
        ...                ('b', None)])
        >>> h.update(0)
        >>> h.log
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

        self.tstart = labtime.time()

        self.columns = [name for name, _ in self.sources]

        self.build_fields()

    def build_fields(self):
        self.fields = [[] for _ in self.columns]
        self.logdict = dict(zip(self.columns, self.fields))
        self.t = self.logdict['Time']

    def update(self, tnow=None):
        if tnow is None:
            self.tnow = labtime.time() - self.tstart
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

    def timeindex(self, t):
        return max(bisect.bisect(self.t, t) - 1, 0)

    def timeslice(self, tstart=0, tend=None, columns=None):
        start = self.timeindex(tstart)
        if tend is None:
            stop = len(self.t) + 1
        # Ensure that we always return at least one time's value
        if tend == tstart:
            stop = start + 1
        if columns is None:
            columns = self.columns
        return [self.logdict[c][start:stop] for c in columns]

    def at(self, t, columns=None):
        """ Return the values of columns at or just before a certain time"""
        return [c[0] for c in self.timeslice(t, t, columns)]

    def after(self, t, columns=None):
        """ Return the values of columns after or just before a certain time"""
        return self.timeslice(t, columns=columns)

    def _dbcheck(self):
        if self.db is None:
            raise NotImplementedError("Sessions not supported without dbfile")
        return True

    def new_session(self):
        self._dbcheck()
        self.db.new_session()
        self.session = self.db.session
        self.tstart = labtime.time()
        self.build_fields()

    def get_sessions(self):
        self._dbcheck()
        return self.db.get_sessions()

    def load_session(self, session):
        self._dbcheck()
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

    def to_csv(self, filename):
        """Output contents of log file to CSV"""
        import csv

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(self.log)


class Plotter:
    def __init__(self, historian, twindow=120, layout=None):
        """Generalised graphical output of a Historian

        :param historian: An instance of the Historian class
        :param twindow: Amount of time to show in the plot
        :param layout: A tuple of tuples indicating how the fields should be
                plotted. For example (("T1", "T2"), ("Q1", "Q2")) indicates
                that there will be two subplots with the two indicated fields
                plotted on each.

                Note: A single plot is specified as (("T1",),) (note the commas)
        """
        import matplotlib.pyplot as plt
        from matplotlib import get_backend
        self.backend = get_backend()
        self.historian = historian
        self.twindow = twindow
        self.last_plot_update = 0
        self.last_plotted_time = 0

        if layout is None:
            layout = tuple((field,) for field in historian.columns[1:])
        self.layout = layout

        line_options = {'where': 'post', 'lw': 2, 'alpha': 0.8}
        self.lines = {}
        self.fig, self.axes = plt.subplots(len(layout), 1, figsize=(8, 1.5*len(layout)),
                                           dpi=80,
                                           sharex=True,
                                           gridspec_kw={'hspace': 0},
                                           squeeze=False)
        self.axes = self.axes[:, 0]
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

        minfps = 3
        maxskip = 50

        clocktime_since_refresh = time.time() - self.last_plot_update
        simtime_since_refresh = self.historian.tnow - self.last_plotted_time

        if clocktime_since_refresh <= 1/minfps and simtime_since_refresh < maxskip:
            return

        tmin = max(self.historian.tnow - self.twindow, 0)
        tmax = max(self.historian.tnow, self.twindow)
        for axis in self.axes:
            axis.set_xlim(tmin, tmax)
        data = self.historian.after(tmin)
        datadict = dict(zip(self.historian.columns, data))
        t = datadict['Time']
        for axis, fields in zip(self.axes, self.layout):
            for field in fields:
                y = datadict[field]
                self.lines[field].set_data(t, y)
            axis.relim()
            axis.autoscale_view()
        self.fig.canvas.draw()
        if self.backend != 'nbAgg':
            self.display.clear_output(wait=True)
            self.display.display(self.fig)

        self.last_plot_update = time.time()
        self.last_plotted_time = self.historian.tnow