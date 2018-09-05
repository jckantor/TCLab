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
                 speedup=1, synced=True, tol=0.5):
        """Parameters:
        connected: If True, connect to a physical TCLab, if False, connecte to
                   TCLabModel
        plot: Use a Plotter
        twindow: (only applicable if plotting) the twindow for the Plotter
        time: total time to run for (used for experiment.clock)
        dbfile: The dbfile to use for the Historian
        speedup: speedup factor to use if not connected.
        synced: Try to run at a fixed factor of real time. If this is False, run
                as fast as possible regardless of the value of speedup.
        tol: Clock tolerance (used for experiment.clock)
        """
        if (speedup != 1 or not synced) and connected:
            raise ValueError('The real TCLab can only run real time.')

        self.connected = connected
        self.plot = plot
        self.twindow = twindow
        self.time = time
        self.dbfile = dbfile
        self.speedup = speedup
        self.synced = synced
        self.tol = tol
        if synced:
            labtime.set_rate(speedup)

        self.lab = None
        self.historian = None
        self.plotter = None

    def __enter__(self):
        if self.connected:
            self.lab = TCLab()
        else:
            self.lab = TCLabModel(synced=self.synced)
        self.historian = Historian(self.lab.sources, dbfile=self.dbfile)
        if self.plot:
            self.plotter = Plotter(self.historian, twindow=self.twindow)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.lab.close()
        self.historian.close()

    def clock(self):
        if self.synced:
            times = clock(self.time, tol=self.tol)
        else:
            times = range(self.time)
        for t in times:
            yield t
            if self.plot:
                self.plotter.update(t)
            else:
                self.historian.update(t)
            if not self.synced:
                self.lab.update(t)


def runexperiment(function, *args, **kwargs):
    """Simple wrapper for Experiment which builds an experiment and calls a
    function in a timed for loop.

    The function will be passed the time and a TCLab instance at every tick of
    the clock.

    The remaining arguments are passed Experiment.
    """
    with Experiment(*args, **kwargs) as experiment:
        for t in experiment.clock():
            function(t, experiment.lab)
    return experiment
