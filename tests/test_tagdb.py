import pytest

from tclab.historian import TagDB

@pytest.fixture()
def db():
    return TagDB()

def test_start_session(db):
    assert db.session is None
    db.start_session()
    assert db.session is not None

def test_record(db):
    db.record(0, "Test", 1)

def test_get(db):
    db.record(0, "Test", 1)
    assert db.get("Test") == [1]

    db.record(1, "Test", 2)
    assert db.get("Test") == [1, 2]