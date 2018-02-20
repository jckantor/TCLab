import pytest
import os

from tclab.gui import NotebookInteraction
from tclab import TCLab, TCLabModel


TRAVIS = "TRAVIS" in os.environ
skip_on_travis = pytest.mark.skipif(TRAVIS,
                                    reason="Can't run this test on Travis")


@pytest.fixture(scope="module", params=[TCLab, TCLabModel])
def lab(request):
    if TRAVIS and request.param is TCLab:
        pytest.skip("Can't use real TCLab on Travis")
    a = request.param()
    yield a
    a.close()


def test_NotebookInteraction_constructor():
    nbUI = NotebookInteraction()


def test_NotebookInteraction_connect(lab):
    nbUI = NotebookInteraction()
    nbUI.connect(lab)
    assert nbUI.lab == lab
    assert nbUI.lab.connected
    nbUI.disconnect()
    assert not nbUI.lab.connected

