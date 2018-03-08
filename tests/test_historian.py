import pytest

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
    b = 1
    h.update(3)

    assert h.logdict['a'][-1] == 1

    log = h.log

    assert len(log) == 3

    assert h.at(1, ['a']) == [0.5]

    assert h.after(2) == [[2, 3], [1, 1], [0, 1]]


def test_implicit_time():
    h = Historian(sources=[('a', lambda: a)])

    a = 0
    h.update()
    a = 1
    h.update()

    assert len(h.log) == 2


def test_wrong_arguments():
    h = Historian(sources=[('a', lambda: [1]),
                           ('b', None)])

    with pytest.raises(ValueError):
        h.update()


def test_logging_list():
    a = 0
    b = 0

    h = Historian(sources=[('a', lambda: (a, b)),
                           ('b', None)])

    a = 0.5
    h.update(1)
    a = 1
    h.update(2)

    assert h.logdict['a'][-1] == 1

    log = h.log

    assert len(log) == 2

    assert h.at(1, ['a']) == [0.5]


def test_sessions():
    h = Historian(sources=[('a', lambda: a)])

    a = 0
    h.update(1)
    a = 2
    h.update(2)

    assert h.session == 1
    assert len(h.get_sessions()) == 1

    h.new_session()

    assert h.session == 2

    a = 2
    h.update(1)
    a = 3
    h.update(2)
    h.update(3)

    assert len(h.get_sessions()) == 2

    assert h.at(1, ['a']) == [2]

    h.load_session(1)

    assert h.at(1, ['a']) == [0]


def test_error_handling():
    h = Historian(sources=[('a', lambda: a)], dbfile=None)

    with pytest.raises(NotImplementedError):
        h.new_session()

    with pytest.raises(NotImplementedError):
        h.get_sessions()

    with pytest.raises(NotImplementedError):
        h.load_session(1)


def test_to_csv(tmpdir):
    outfile = tmpdir.join('test.csv')

    a = 0
    b = 0

    h = Historian(sources=[('a', lambda: (a, b)),
                           ('b', None)])

    a = 0.5
    h.update(1)
    a = 1
    h.update(2)

    h.to_csv(outfile)

    import csv
    lines = list(csv.reader(outfile.open()))

    assert len(lines) == 3
    assert lines[0] == h.columns
    assert lines[1:] == [[str(i) for i in line] for line in h.log]
