from tclab import Historian


def test_constructor():
    h = Historian(sources=())


def test_logging():
    a = 0
    b = 0

    h = Historian(sources=[('a', lambda: a),
                           ('b', lambda: b)])

    a = 0.5
    h.update(1)
    a = 1
    h.update(2)

    assert h.logdict['a'][-1] == 1

    log = h.log

    assert len(log) == 2

    assert h.at(1, ['a']) == [0.5]

