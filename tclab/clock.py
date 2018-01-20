import time


class TCLabClockError(RuntimeError):
    """Provide exception handling of TCLab clock sync errors."""
    def __init__(self, message):
        RuntimeError.__init__(self, message)


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
    start_time = time.time()
    prev_time = start_time
    fuzz = 0.004
    k = 0
    while (prev_time-start_time) <= tperiod + tol:
        if strict and (abs(prev_time - start_time - k * tstep) > tol):
            raise TCLabClockError("Clock lost real time synchronization.")
        yield round(prev_time - start_time, 1)
        if strict:
            tsleep = (k+1)*tstep - (time.time() - start_time) - fuzz
        else:
            tsleep = tstep - (time.time() - prev_time) - fuzz
        if tsleep >= fuzz:
            time.sleep(tsleep)
        prev_time = time.time()
        k += 1
