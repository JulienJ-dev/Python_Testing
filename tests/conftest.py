import pytest

import server


@pytest.fixture
def client():
    server.app.config.update(TESTING=True)
    return server.app.test_client()
