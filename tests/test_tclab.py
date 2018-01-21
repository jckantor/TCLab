import pytest

from tclab import TCLabSurrogate, TCLab


@pytest.fixture(scope="module", params=[TCLab, TCLabSurrogate])
def lab(request):
    a = request.param()
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
    assert lab.LED(50) == 50


def settertests(method):
    assert method(-10) == 0
    assert method(50) == 50
    assert method(120) == 100
    assert 0 <= method() <= 100


def test_Q1(lab):
    settertests(lab.Q1)


def test_Q2(lab):
    settertests(lab.Q2)
