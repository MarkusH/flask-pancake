from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from flask_pancake import FlaskPancake, Sample

if TYPE_CHECKING:
    from flask import Flask


def test_sample(app: Flask):
    feature = Sample("feature", 42)

    assert app.extensions["redis"].get("SAMPLE:pancake:FEATURE") is None

    with mock.patch("random.uniform", return_value=42.00001):
        assert feature.is_active() is False
    assert app.extensions["redis"].get("SAMPLE:pancake:FEATURE") == b"42"
    with mock.patch("random.uniform", return_value=42):
        assert feature.is_active() is True
        feature.set(10)
        assert feature.is_active() is False

    feature.clear()
    assert app.extensions["redis"].get("SAMPLE:pancake:FEATURE") is None


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
        ValueError, match=r"Value for sample X must be in the range \[0, 100\]\.",
    ):
        sample.set(value)
