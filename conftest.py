import os
import pytest

os.environ.setdefault("SUPERSONIC_LOG_FILE", "supersonic.log")
os.environ.setdefault("HEALTH_5XX_WINDOW_SEC", "120")
os.environ.setdefault("DOCTOR_KEY", "testkey")

from serve_pdfs import app as flask_app


@pytest.fixture(scope="session")
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def doctor_headers():
    return {"X-Doctor-Key": os.environ["DOCTOR_KEY"]}
