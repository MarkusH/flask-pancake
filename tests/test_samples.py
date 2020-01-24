from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

from flask_pancake import FlaskPancake, Sample
from flask_pancake.constants import EXTENSION_NAME

if TYPE_CHECKING:
    from flask import Flask


def test_sample(app: Flask):
    feature = Sample("feature", 42)

    assert app.extensions["redis"].get("SAMPLE:FEATURE") is None

    with mock.patch("random.uniform", return_value=42.00001):
        assert feature.is_active() is False
    assert app.extensions["redis"].get("SAMPLE:FEATURE") == b"42"
    with mock.patch("random.uniform", return_value=42):
        assert feature.is_active() is True

    feature.clear()
    assert app.extensions["redis"].get("SAMPLE:FEATURE") is None


def test_key(app: Flask):
    sample = Sample("my-sample", True)
    app.extensions[EXTENSION_NAME].get_user_id_func = lambda: "some-uid"
    assert sample.key == "SAMPLE:MY-SAMPLE"


def test_scoped_key(app: Flask):
    FlaskPancake(app, name="scopy")
    sample = Sample("my-sample", True, extension="scopy")
    app.extensions["scopy"].get_user_id_func = lambda: "some-uid"
    app.extensions["scopy"].get_user_id_func = lambda: "scopy-uid"
    assert sample.key == "SAMPLE:MY-SAMPLE:scopy"
