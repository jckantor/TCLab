import pytest

from tclab import setup, TCLab, TCLabModel


def test_connected():
    assert TCLab == setup(connected=True, speedup=1)
    assert TCLabModel == setup(connected=False, speedup=2)
    assert TCLabModel == setup(connected=False, speedup=10)


def test_connected_error():
    with pytest.raises(ValueError):
        setup(connected=True, speedup=2)
    with pytest.raises(ValueError):
        setup(connected=True, speedup=10)


