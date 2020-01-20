import pytest
from flask import Flask
from flask_redis import FlaskRedis

from flask_pancake import EXTENSION_NAME, FlaskPancake


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


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def flask_pancake_cleanup(app: Flask):
    def inner():
        flask_pancake: FlaskPancake = app.extensions[EXTENSION_NAME]
        for flag in flask_pancake.flags.values():
            flag.clear()
            flag.clear_all_users()
        for switch in flask_pancake.switches.values():
            switch.clear()
        for sample in flask_pancake.samples.values():
            sample.clear()

    inner()
    yield
    inner()
