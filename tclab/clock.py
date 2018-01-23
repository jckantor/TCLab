import time as original_time

SPEEDUP = 1


def setup(speedup=1):
    global SPEEDUP
    SPEEDUP = speedup


def time():
    return SPEEDUP*original_time.time()


def sleep(tsleep):
    return original_time.sleep(tsleep/SPEEDUP)


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
    curr_time = start_time = time()
    fuzz = 0.01
    k = 0
    while (curr_time - start_time) <= (tperiod - tstep) + tol + fuzz:
        yield round(curr_time - start_time, 1)
        if strict:
            tsleep = (k+1)*tstep - (time() - start_time) - fuzz
        else:
            tsleep = tstep - (time() - curr_time) - fuzz
        if tsleep >= fuzz:
            sleep(tsleep)
        curr_time = time()
        k += 1
        if strict and (abs(curr_time - start_time - k * tstep) > tol + fuzz):
            raise RuntimeError("TCLab clock lost real time synchronization.")

    yield round(curr_time - start_time, 1)
