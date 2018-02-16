import pytest
import time

from tclab import clock, Scaletime


def test_initialize_time():
    """Instances created at different times should have the same _known_time."""
    a = Scaletime()
    time.sleep(2)
    b = Scaletime()
    assert a._known_time == b._known_time


def test_timemethod():
    """Instances created at different times should report the same scaled time."""
    a = Scaletime()
    time.sleep(2)
    b = Scaletime()
    assert abs(b.time() - a.time()) < 0.01


def test_scale():
    """Change scale factors."""
    sf = 2
    delay = 1
    a = Scaletime()
    tic = a.time()
    a.scale(sf)
    time.sleep(delay)
    toc = a.time()
    assert abs(toc - tic - sf * delay) < 0.05


def test_sleep():
    sf = 5
    sdelay = 10
    a = Scaletime()
    a.scale(sf)
    stic = a.time()
    tic = time.time()
    a.sleep(sdelay)
    stoc = a.time()
    toc = time.time()
    assert abs(stoc - stic - sdelay) < 0.1
    assert abs(toc - tic - sdelay/sf) < 0.1


# need a test for: error on zero or negative scale factor


def test_reset():
    a  = Scaletime()
    time.sleep(2)
    a.reset()
    assert a.time() < 0.01
    assert a._elapsed_time == 0


def test_stop():
    a = Scaletime()
    a.stop()
    tic = a.time()
    time.sleep(1)
    toc = a.time()
    assert tic==toc
    assert a._running == False


def test_start():
    a = Scaletime()
    a.scale(1)
    a.stop()
    tic = a.time()
    atic = a._known_time
    time.sleep(2)
    a.start()
    toc = a.time()
    atoc = a._known_time
    assert abs(toc - tic) < 0.1
    assert abs(atoc - atic - 2) < 0.1
    assert a._running == True
