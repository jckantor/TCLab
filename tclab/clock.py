import time as realtime
import gc

SPEEDUP = 1
tnow = 0


def setup(speedup=1):
    global SPEEDUP
    SPEEDUP = speedup


def time():
    """Returns current clock time."""
    return tnow

def setnow(t):
    global tnow
    tnow = t

def clock(tperiod, tstep=1, tol=0.25):
    """Generator providing time values in sync with real time clock.

    Args:
        tperiod (float): Time interval for clock operation in seconds.
        tstep (float): Time step.
        strict (bool): False turns off real-time synchronization.
        tol (float): Maximum permissible deviation from real time.

    Yields:
        float: The next time step rounded to nearest 10th of a second.

    Raises:
         TCLabClockError: If clock becomes more than `tol` out of phase
             with real time clock.
    """
    global tnow
    setnow(0)
    start_time = SPEEDUP * realtime.time()
    fuzz = 0.003
    k = 0
    while tnow <= tperiod - tstep + tol:
        yield round(tnow, 1)
        k += 1
        if SPEEDUP < 10:
            tsleep = k * tstep\
                     - (SPEEDUP * realtime.time() - start_time)\
                     - SPEEDUP * fuzz
            gcold = gc.isenabled()
            gc.disable()
            try:
                realtime.sleep(max(0, tsleep/SPEEDUP))
            finally:
                if gcold:
                    gc.enable()
            setnow(SPEEDUP * realtime.time() - start_time)
            if abs(tnow - k * tstep) > tol:
                raise RuntimeError("TCLab clock lost synchronization.")
        else:
            tnow = k * tstep

    yield round(tnow, 1)
