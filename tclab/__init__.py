from .tclab import TCLab, TCLabModel
from .historian import Historian, Plotter
from .experiment import Experiment, runexperiment
from .labtime import clock, labtime


def setup(connected=True, rate=1):
    """Set up a lab session with simple switching between real and model lab

    The idea of this function is that you will do

    >>> lab = setup(connected=True)

    to obtain a TCLab class reference. If `connected=False` then you will
    receive a TCLabModel class reference. This allows you to switch between
    the model and the real lab in your code easily.

    The rate option can only be used when `connected=False` and is the
    ratio by which the lab clock will be sped up relative to real time
    during the simulation.

    For example

    >>> lab = setup(connected=False, rate=2)

    will run the lab clock at twice real time (which means that the whole simulation
    will take half the time it would if connected to a real device).
    """

    if connected:
        lab = TCLab
        if rate != 1:
            raise ValueError('The real lab must run in real time')
    else:
        lab = TCLabModel
        if rate < 0:
            raise ValueError('speedup must be positive. '
                             'You passed rate={}'.format(rate))

    labtime.set_rate(rate)
    return lab

