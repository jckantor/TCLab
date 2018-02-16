import time as time


class Scaletime():
    _known_time = time.time()
    _scalefactor = 1
    _elapsed_time = 0
    _running = True


    @classmethod
    def time(cls):
        """Return time elapsed since class definition in scaled units."""
        return cls._elapsed_time + int(
            cls._running) * cls._scalefactor * (
                           time.time() - cls._known_time)


    @classmethod
    def scale(cls, scalefactor):
        """Change the time scale factor, i.e., ratio of scaled time rate to real time."""
        cls._elapsed_time = cls.time()
        cls._known_time = time.time()
        cls._scalefactor = scalefactor


    @classmethod
    def sleep(cls, delay):
        """Sleep for a period delay in scaled time units."""
        if cls._scalefactor == 0:
            raise RuntimeError(
                "Can't sleep when scaled clock is stopped.")
        time.sleep(delay / cls._scalefactor)


    @classmethod
    def reset(cls):
        """Reset scaled time to zero."""
        cls._known_time = time.time()
        cls._elapsed_time = 0


    @classmethod
    def stop(cls):
        """Stop scaled time clock."""
        cls._elapsed_time = cls.time()
        cls._known_time = time.time()
        cls._running = False


    @classmethod
    def start(cls):
        """Restart scale time clock using previous scale factor and elapsed time."""
        cls._known_time = time.time()
        cls._running = True


clocktime = Scaletime()


def clock(tperiod, tstep=1, tol=0.25):
    """Generator providing time values in sync with real time clock.

    Args:
        tperiod (float): Time interval for clock operation in seconds.
        tstep (float): Time step.
        tol (float): Maximum permissible deviation from real time.

    Yields:
        float: The next time step rounded to nearest 10th of a second.
    """
    clocknow = 0
    clockstart = clocktime.time()
    while clocknow <= tperiod - tstep + tol:
        yield round(clocknow, 1)
        tsleep = tstep - (clocktime.time() - clockstart) % tstep
        clocktime.sleep(tsleep)
        clocknow = (clocktime.time() - clockstart)

    yield round(clocknow, 1)
