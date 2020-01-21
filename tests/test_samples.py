from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

from flask_pancake import Sample

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
