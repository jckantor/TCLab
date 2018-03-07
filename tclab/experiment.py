from .tclab import TCLab, TCLabModel
from .historian import Historian, Plotter
from .labtime import labtime, clock


class Experiment:
    """Utility class for running experiments on the TCLab

    The class is designed to be used as a context. On initialisation
    it will automatically connect to the TCLab, create a Historian and Plotter
    and provide a `.clock` method.

    >>> with Experiment(connected=False, plot=False, time=20) as experiment:
    ...     for t in experiment.clock():
    ...         experiment.lab.Q1(100 if t < 100 else 0)
    ... # doctest: +SKIP
    ... # doctest: +ELLIPSIS
    TCLab version ...
    Simulated TCLab
    TCLab Model disconnected successfully.

    Once the experiment has run, you can access `experiment.historian` to see
    the results from the simulation.

    """

    def __init__(self, connected=True, plot=True,
                 twindow=200, time=500,
                 dbfile=':memory:',
                 speedup=1):
        """Parameters:
        connected: If True, connect to a physical TCLab, if False, connecte to
                   TCLabModel
        plot: Use a Plotter
        twindow: (only applicable if plotting) the twindow for the Plotter
        time: total time to run for (used for experiment.clock)
        dbfile: The dbfile to use for the Historian
        speedup: speedup factor to use if not connected. If this is zero, the
                 experiment will run as fast as possible.
        """
        if speedup != 1 and connected:
            raise ValueError('The real TCLab can only run real time.')

        self.connected = connected
        self.plot = plot
        self.twindow = twindow
        self.time = time
        self.dbfile = dbfile
        self.speedup = speedup
        if speedup != 0:
            labtime.set_rate(speedup)

        self.lab = None
        self.historian = None
        self.plotter = None


    def __enter__(self):
        if self.connected:
            self.lab = TCLab()
        else:
            self.lab = TCLabModel()
        self.historian = Historian(self.lab.sources, dbfile=self.dbfile)
        if self.plot:
            self.plotter = Plotter(self.historian, twindow=self.twindow)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.lab.close()
        self.historian.close()

    def clock(self):
        if self.speedup != 0:
            times = clock(self.time)
        else:
            times = range(self.time)
        for t in times:
            yield t
            if self.plot:
                self.plotter.update(t)
            else:
                self.historian.update(t)
            if self.speedup == 0:
                self.lab.update(t)


def runexperiment(function, connected=True, plot=True,
                  twindow=200, time=500,
                  dbfile=':memory:',
                  speedup=1):
    with Experiment(connected, plot, twindow, time, dbfile, speedup) as experiment:
        for t in experiment.clock():
            function(t, experiment.lab)
    return experiment
