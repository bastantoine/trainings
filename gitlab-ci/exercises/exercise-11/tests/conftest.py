import pytest

from accounting.app import setup_app


@pytest.fixture()
def app():
    app = setup_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
