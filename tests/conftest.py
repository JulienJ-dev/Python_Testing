import copy

import pytest

import server


INITIAL_CLUBS = copy.deepcopy(server.clubs)
INITIAL_COMPETITIONS = copy.deepcopy(server.competitions)


@pytest.fixture(autouse=True)
def reset_data(monkeypatch):
    monkeypatch.setattr(server, "clubs", copy.deepcopy(INITIAL_CLUBS))
    monkeypatch.setattr(server, "competitions", copy.deepcopy(INITIAL_COMPETITIONS))


@pytest.fixture
def client():
    server.app.config.update(TESTING=True)
    return server.app.test_client()
