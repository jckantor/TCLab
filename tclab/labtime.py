import time as time


class Labtime():
    __realtime = time.time()
    __labtime = 0
    __rate = 1
    __running = True

    @property
    def running(self):
        """Returns variable indicating whether labtime is running."""
        return self.__class__.__running

    def time(self):
        """Return current labtime."""
        if self.running:
            elapsed = time.time() - self.__class__.__realtime
            return self.__class__.__labtime + self.__class__.__rate * elapsed
        else:
            return self.__class__.__labtime

    def set_rate(self, rate=1):
        """Set the rate of labtime relative to real time."""
        if rate <= 0:
            raise ValueError("Labtime rates must be positive.")
        self.__class__.__labtime = self.time()
        self.__class__.__realtime = time.time()
        self.__class__.__rate = rate

    def get_rate(self):
        """Return the rate of labtime relative to real time."""
        return self.__class__.__rate

    def sleep(self, delay):
        """Sleep in labtime for a period delay."""
        if self.__class__.__running:
            time.sleep(delay / self.__class__.__rate)
        else:
            raise RuntimeWarning("sleep is not valid when labtime is stopped.")

    def stop(self):
        """Stop labtime."""
        self.__class__.__labtime = self.time()
        self.__class__.__realtime = time.time()
        self.__class__.__running = False

    def start(self):
        """Restart labtime."""
        self.__class__.__realtime = time.time()
        self.__class__.__running = True

    def reset(self, val=0):
        """Reset labtime to a specified value."""
        self.__class__.__labtime = val
        self.__class__.__realtime = time.time()


labtime = Labtime()


# for backwards compatability
def setnow(tnow=0):
    labtime.reset(tnow)


def clock(period, step=1, tol=0.5, adaptive=True):
    """Generator providing time values in sync with real time clock.

    Args:
        tperiod (float): Time interval for clock operation in seconds.
        tstep (float): Time step.
        tol (float): Maximum permissible deviation from real time.

    Yields:
        float: The next time step rounded to nearest 10th of a second.
    """
    start = labtime.time()
    now = 0

    while now <= period - step + tol:
        yield round(now, 1)
        elapsed = labtime.time() - start - now
        if labtime.get_rate() != 1:
            if elapsed > step:
                labtime.set_rate(0.8*labtime.get_rate()*step/elapsed)
            elif (elapsed < 0.5 * step) & (labtime.get_rate() < 50):
                labtime.set_rate(1.2*labtime.get_rate())
        else:
            if elapsed > step + tol:
                raise RuntimeError('Labtime clock lost synchronization with real time.')
        labtime.sleep(step - (labtime.time() - start) % step)
        now = labtime.time() - start

    yield round(now, 1)
