import pytest

from tclab import TCLab

@pytest.fixture(scope="module")
def lab():
    a = TCLab()
    yield a
    a.close()

def test_constructor():
    a = TCLab()
    a.close()

def test_context():
    with TCLab() as _:
        pass

def test_T1(lab):
    assert -10 < lab.T1 < 110

def test_T2(lab):
    assert -10 < lab.T2 < 110

def test_LED(lab):
    lab.LED(100)

def test_Q1_set(lab):
    lab.Q1(100)

def test_Q2_set(lab):
    lab.Q2(100)

def test_Q1_read(lab):
    assert 0 <= lab.Q1() <= 100

def test_Q2_read(lab):
    assert 0 <= lab.Q2() <= 100

