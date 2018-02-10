from .tclab import TCLab, TCLabModel
from .clock import clock, time
from .historian import Historian, Plotter
from .experiment import Experiment, runexperiment


def setup(connected=True, speedup=1):
    """Set up a lab session with simple switching between real and model lab

    The idea of this function is that you will do

    >>> lab = setup(connected=True)

    to obtain a TCLab class reference. If `connected=False` then you will
    receive a TCLabModel class reference. This allows you to switch between
    the model and the real lab in your code easily.

    The speedup option can only be used when `connected=False` and is a factor
    by which the clock will be sped up during the simulation.

    For example

    >>> lab = setup(connected=False, speedup=2)

    will run the clock at twice real time (which means that the whole simulation
    will take half the time it would if connected to a real device).
    """
    from .clock import setup as clocksetup

    if connected:
        lab = TCLab
        if speedup != 1:
            raise ValueError('The real lab must run in real time')
    else:
        lab = TCLabModel
        if speedup < 0:
            raise ValueError('speedup must be positive. '
                             'You passed speedup={}'.format(speedup))

    clocksetup(speedup=speedup)
    return lab

