from __future__ import annotations

from unittest import mock

import pytest
from flask import Flask, g

from flask_pancake import FlaskPancake, Sample


def test_sample(app: Flask):
    feature = Sample("feature", 42)

    assert app.extensions["redis"].get("SAMPLE:pancake:FEATURE") is None

    with mock.patch("random.uniform", return_value=42.00001):
        assert feature.is_active() is False

    # Remove the tracked is_active state from `g`:
    g.pop("pancakes", None)

    assert app.extensions["redis"].get("SAMPLE:pancake:FEATURE") == b"42"
    with mock.patch("random.uniform", return_value=42):
        assert feature.is_active() is True

        # Remove the tracked is_active state from `g`:
        g.pop("pancakes", None)

        feature.set(10)
        assert feature.is_active() is False

    assert app.extensions["redis"].set("SAMPLE:pancake:FEATURE", b"13")
    assert feature.get() == 13

    feature.clear()
    assert app.extensions["redis"].get("SAMPLE:pancake:FEATURE") is None


def test_store_load(app: Flask):
    feature = Sample("feature", 100)
    assert feature.is_active() is True
    assert g.pancakes["pancake"]["feature"] is True

    feature.set(0)

    assert feature.is_active() is True
    assert g.pancakes["pancake"]["feature"] is True

    # Remove the tracked is_active state from `g`:
    g.pop("pancakes", None)

    with mock.patch("random.uniform", return_value=42):
        assert feature.is_active() is False

    assert g.pancakes["pancake"]["feature"] is False


def test_key(app: Flask):
    sample = Sample("my-sample", True)
    assert sample.key == "SAMPLE:pancake:MY-SAMPLE"


def test_scoped_key(app: Flask):
    FlaskPancake(app, name="scopy")
    sample = Sample("my-sample", True, extension="scopy")
    assert sample.key == "SAMPLE:scopy:MY-SAMPLE"


@pytest.mark.parametrize("value", [-0.000001, 100.00001])
def test_out_of_bounds_default(value):
    with pytest.raises(
        ValueError,
        match=r"Default value for sample X must be in the range \[0, 100\]\.",
    ):
        Sample("X", value)


@pytest.mark.parametrize("value", [-0.000001, 100.00001])
def test_sample_out_of_bounds_set(value):
    sample = Sample("X", 42)
    with pytest.raises(
        ValueError,
        match=r"Value for sample X must be in the range \[0, 100\]\.",
    ):
        sample.set(value)
