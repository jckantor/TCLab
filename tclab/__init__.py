from .tclab import TCLab, TCLabModel
from .clock import clock
from .historian import Historian, Plotter

def setup(connected=True, speedup=1):
    from .clock import setup as clocksetup

    if connected:
        lab = TCLab
        if speedup != 1:
            raise ValueError("The real lab must run in real time")
    else:
        lab = TCLabModel
        if speedup < 0:
            raise ValueError("")

    clocksetup(speedup=speedup)
    return lab