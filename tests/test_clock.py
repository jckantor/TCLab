import pytest
import time

from tclab import clock


def test_generator():
    assert [_ for _ in clock(3)] == [0.0, 1.0, 2.0, 3.0]


def test_tstep():
    assert [_ for _ in clock(4, 1.5)] == [0.0, 1.5, 3.0]


def test_tolerance():
    for _ in clock(1, tol=0.25):
        time.sleep(1.2)
    for t in clock(5, 1, tol=0.25):
        if 0.5 < t < 2.5:
            time.sleep(1.1)
    assert t == 5.0


def test_sync():
    for t in clock(5, 1, tol=0.25):
        if 0.5 < t < 2.5:
            time.sleep(1.1)
    assert t == 5.0

