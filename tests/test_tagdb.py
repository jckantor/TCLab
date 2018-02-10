import pytest

from tclab.historian import TagDB


@pytest.fixture()
def db():
    return TagDB()


def test_start_session(db):
    assert db.session is None
    db.new_session()
    assert db.session is not None


def test_record(db):
    db.record(0, "Test", 1)


def test_get(db):
    db.record(0, "Test", 1)
    assert db.get("Test") == [(0, 1)]

    db.record(1, "Test", 2)
    assert db.get("Test") == [(0, 1), (1, 2)]


def test_get_sessions(db):
    db.new_session()
    db.new_session()
    sessions = db.get_sessions()

    assert len(sessions) == 2
    assert sessions[0][0] == 1
    assert sessions[1][0] == 2
