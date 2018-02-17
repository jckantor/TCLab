import pytest
import time

from tclab import labtime, clock

# labtime tests

def test_import():
    assert labtime.get_rate() == 1
    assert labtime.running


def test_time():
    delay = 1
    labtime.set_rate(1)
    tic = labtime.time()
    time.sleep(delay)
    toc = labtime.time()
    assert abs(delay - (toc-tic)) < 0.05


def test_set_rate():
    labtime.set_rate(2)
    assert labtime.get_rate() == 2
    with pytest.raises(ValueError):
        labtime.set_rate(0)
    with pytest.raises(ValueError):
        labtime.set_rate(-1)


def test_rate():
    sf = 2
    delay = 1
    labtime.set_rate(sf)
    tic = labtime.time()
    time.sleep(delay)
    toc = labtime.time()
    assert abs(toc - tic - sf * delay) < 0.05


def test_stop():
    labtime.stop()
    tic = labtime.time()
    time.sleep(1)
    toc = labtime.time()
    assert tic == toc
    assert labtime.running == False


def test_start():
    delay = 1
    labtime.set_rate(1)
    labtime.stop()
    tic = labtime.time()
    labtime.start()
    time.sleep(delay)
    toc = labtime.time()
    assert abs(toc - tic - delay) < 0.1
    assert labtime.running == True


def test_reset():
    time.sleep(2)
    labtime.reset()
    assert labtime.time() < 0.01
    labtime.reset(10)
    assert labtime.time() < 10.01


def test_sleep():
    sf = 5
    sdelay = 10
    labtime.set_rate(sf)
    stic = labtime.time()
    tic = time.time()
    labtime.sleep(sdelay)
    stoc = labtime.time()
    toc = time.time()
    assert abs(stoc - stic - sdelay) < 0.1
    assert abs(toc - tic - sdelay/sf) < 0.1


def test_sleep_exception():
    with pytest.raises(RuntimeError):
        labtime.stop()
        labtime.sleep(1)
    labtime.start()


@pytest.mark.parametrize("rate", [1, 2, 5, 10, 20, 50])
def test_generator(rate):
    labtime.set_rate(rate)
    assert [round(_) for _ in clock(3)] == [0, 1, 2, 3]


@pytest.mark.parametrize("rate", [1, 2, 5, 10, 20, 50])
def test_tstep(rate):
    labtime.set_rate(rate)
    assert [round(_) for _ in clock(4, 2)] == [0, 2, 4]


@pytest.mark.parametrize("rate", [1, 2, 5, 10, 20, 50])
def test_tolerance(rate):
    labtime.set_rate(rate)
    for _ in clock(1, tol=0.25):
        labtime.sleep(1.2)
    for t in clock(5, 1, tol=0.25):
        if 0.5 < t < 2.5:
            labtime.sleep(1.1)
    assert round(t) == 5.0


@pytest.mark.parametrize("rate", [1, 2, 5, 10, 20, 50])
def test_sync(rate):
    labtime.set_rate(rate)
    for t in clock(5, 1, tol=0.25):
        if 0.5 < t < 2.5:
            labtime.sleep(1.1)
    assert round(t) == 5.0

