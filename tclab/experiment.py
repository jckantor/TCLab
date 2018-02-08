from .tclab import TCLab, TCLabModel


class Experiment:
    def __init__(self, connected=True, plot=True, twindow=200, time=2000):
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
        self.historian = Historian(self.lab)
        if self.plot:
            self.plotter = Plotter(self.historian)

        return self

    def __exit__(self):
        self.lab.close()
        self.historian.close()


def runexperiment():
    pass
