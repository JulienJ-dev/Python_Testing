import copy

import pytest

import server


TEST_CLUBS = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
    {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
]

TEST_COMPETITIONS = [
    {
        "name": "Future Games",
        "date": "2099-03-27 10:00:00",
        "numberOfPlaces": "25",
    },
    {
        "name": "Past Games",
        "date": "2000-03-27 10:00:00",
        "numberOfPlaces": "10",
    },
]


@pytest.fixture(autouse=True)
def reset_data(monkeypatch, tmp_path):
    """Give every test fresh in-memory data."""
    monkeypatch.setattr(server, "clubs", copy.deepcopy(TEST_CLUBS))
    monkeypatch.setattr(server, "competitions", copy.deepcopy(TEST_COMPETITIONS))
    monkeypatch.setattr(server, "STATE_FILE", tmp_path / "state.json")


@pytest.fixture
def client():
    server.app.config.update(TESTING=True)
    return server.app.test_client()


@pytest.fixture
def logged_in_client(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    return client
