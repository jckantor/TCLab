import time


class TCLabClockError(RuntimeError):
    """Error class to allow exception handling of clock sync errors."""
    def __init__(self, message):
        RuntimeError.__init__(self, message)


def clock(tperiod, tstep=1, strict=True, tol=0.1):
    start_time = time.time()
    prev_time = start_time
    fuzz = 0.004
    k = 0
    while (prev_time-start_time) <= tperiod + fuzz:
        if strict and ((prev_time - start_time) > (k*tstep + tol)):
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
