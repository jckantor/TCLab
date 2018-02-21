import pytest
import os
from unittest import mock

from tclab.gui import NotebookInteraction, actionbutton, NotebookUI


# add tests for slider and labelled values


def test_NotebookInteraction_constructor():
    nbUI = NotebookInteraction()


def test_NotebookInteraction_connect():
    lab = mock.Mock()
    nbUI = NotebookInteraction()
    nbUI.connect(lab)
    assert nbUI.lab == lab
    assert nbUI.lab.connected
    nbUI.disconnect()
    assert not nbUI.lab.connected


def test_NotebookInteraction_start():
    nbUI = NotebookInteraction()
    with pytest.raises(NotImplementedError):
        nbUI.start()


def test_NotebookInteraction_stop():
    nbUI = NotebookInteraction()
    with pytest.raises(NotImplementedError):
        nbUI.stop()


def test_NotebookInteraction_update():
    nbUI = NotebookInteraction()
    with pytest.raises(TypeError):
        nbUI.update()
    with pytest.raises(NotImplementedError):
        nbUI.update(0)


def test_NotebookUI_constructor():
    controller = mock.Mock()
    nbUI = NotebookUI(controller)


#  to go further, need to programmatically click ipywidgets


def test_NotebookUI_start():
    controller = mock.Mock()
    nbUI = NotebookUI(controller)
