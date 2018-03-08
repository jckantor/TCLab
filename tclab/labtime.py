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
        adaptive (Boolean): If true, and if the rate != 1, then the labtime
            rate is adjusted to maximize simulation speed.

    Yields:
        float: The next time step rounded to nearest 10th of a second.
    """
    start = labtime.time()
    now = 0

    while now <= period - step + tol:
        yield round(now, 1)
        elapsed = labtime.time() - start - now
        rate = labtime.get_rate()
        if (rate != 1) and adaptive:
            if elapsed > step:
                labtime.set_rate(0.8 * rate * step / elapsed)
            elif (elapsed < 0.5 * step) & (rate < 50):
                labtime.set_rate(1.25 * rate)
        else:
            if elapsed > step + tol:
                message = ('Labtime clock lost synchronization with real time. '
                           'Step size was {} s, but {:.2f} s elapsed '
                           '({:.2f} too long). Consider increasing step.')
                raise RuntimeError(message.format(step, elapsed, elapsed-step))
        labtime.sleep(step - (labtime.time() - start) % step)
        now = labtime.time() - start

    yield round(now, 1)
