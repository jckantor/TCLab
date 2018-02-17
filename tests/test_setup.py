import pytest

from tclab import setup, TCLab, TCLabModel


def test_connected():
    assert TCLab == setup(connected=True, rate=1)
    assert TCLabModel == setup(connected=False, rate=2)
    assert TCLabModel == setup(connected=False, rate=10)


def test_connected_error():
    with pytest.raises(ValueError):
        setup(connected=True, rate=2)
    with pytest.raises(ValueError):
        setup(connected=True, rate=10)
    with pytest.raises(ValueError):
        setup(connected=False, rate=0)
    with pytest.raises(ValueError):
        setup(connected=False, rate=-1)


