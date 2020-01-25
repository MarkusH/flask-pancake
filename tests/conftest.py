import pytest
from flask import Flask
from flask_redis import FlaskRedis

from flask_pancake import FlaskPancake
from flask_pancake.registry import registry


@pytest.fixture
def _app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    FlaskRedis(app)
    FlaskPancake(app)
    yield app


@pytest.fixture
def app(_app):
    with _app.app_context():
        yield _app


@pytest.fixture(autouse=True)
def flask_pancake_cleanup(app: Flask):
    app.extensions["redis"].flushall()
    registry.__clear__()
    yield
    app.extensions["redis"].flushall()
    registry.__clear__()
