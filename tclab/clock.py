import time as original_time
import gc

SPEEDUP = 1
tnow = 0


def setup(speedup=1):
    global SPEEDUP
    SPEEDUP = speedup


def time():
    return tnow


def scaledtime():
    return SPEEDUP*original_time.time()


def clock(tperiod, tstep=1, strict=True, tol=0.1):
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
    tnow = 0
    start_time = scaledtime()
    fuzz = 0.01
    k = 0
    while tnow <= tperiod - tstep + tol + fuzz:
        yield round(tnow, 1)
        if SPEEDUP < 10:
            if strict:
                tsleep = max(0, (k + 1) * tstep - (scaledtime() - start_time) - fuzz)
            else:
                tsleep = max(0, tstep - (scaledtime() - start_time - tnow) - fuzz)
            gcold = gc.isenabled()
            gc.disable()
            try:
                if tsleep >= fuzz:
                    original_time.sleep(tsleep/SPEEDUP)
            finally:
                if gcold:
                    gc.enable()
            tnow = scaledtime() - start_time
        else:
            tnow = (k+1)*tstep
        k += 1
        if strict and (abs(tnow - k * tstep) > tol + fuzz):
            raise RuntimeError("TCLab clock lost real time synchronization.")
    yield round(tnow, 1)
