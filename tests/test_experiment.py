import pytest

from tclab.experiment import Experiment, runexperiment


def test_constructor():
    e = Experiment(connected=False, plot=False)


def test_experiment_context():
    with Experiment(connected=False, plot=False) as experiment:
        pass


def test_experiment_run():
    with Experiment(connected=False, plot=False) as experiment:
        for t in experiment.clock():
            pass

@pytest.mark.skip
def test_runexperiment():
    def function(t, lab):
        pass

    runexperiment(function, connected=False, plot=False, time=10)