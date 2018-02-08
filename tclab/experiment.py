from .tclab import TCLab, TCLabModel
from .historian import Historian, Plotter
from .clock import clock


class Experiment:
    def __init__(self, connected=True, plot=True, twindow=200, time=500):
        self.connected = connected
        self.plot = plot
        self.twindow = twindow
        self.time = time

        self.lab = None
        self.historian = None
        self.plot = None

    def __enter__(self):
        if self.connected:
            self.lab = TCLab()
        else:
            self.lab = TCLabModel()
        self.historian = Historian(self.lab.sources)
        if self.plot:
            self.plotter = Plotter(self.historian)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.lab.close()
        self.historian.close()

    def clock(self):
        for t in clock(self.time):
            if self.plot:
                self.plotter.update(t)
            else:
                self.historian.update(t)


def runexperiment(function, connected=True, plot=True, twindow=200, time=500):
    with Experiment(connected, plot, twindow, time) as experiment:
        for t in experiment.clock():
            function(t, experiment.lab)
    return experiment
