from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flask_pancake import FlaskPancake, Switch
from flask_pancake.constants import RAW_FALSE, RAW_TRUE

if TYPE_CHECKING:
    from flask import Flask


def test_switch(app: Flask):
    off = Switch("default_off", False)
    on = Switch("default_on", True)

    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_OFF") is None
    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_ON") is None

    assert off.is_active() is False
    assert on.is_active() is True

    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_OFF") == RAW_FALSE
    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_ON") == RAW_TRUE

    off.enable()
    on.disable()

    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_OFF") == RAW_TRUE
    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_ON") == RAW_FALSE

    assert off.is_active() is True
    assert on.is_active() is False

    off.clear()
    assert app.extensions["redis"].get("SWITCH:pancake:DEFAULT_OFF") is None


def test_key(app: Flask):
    switch = Switch("my-switch", True)
    assert switch.key == "SWITCH:pancake:MY-SWITCH"


def test_scoped_key(app: Flask):
    FlaskPancake(app, name="scopy")
    switch = Switch("my-switch", True, extension="scopy")
    assert switch.key == "SWITCH:scopy:MY-SWITCH"


def test_out_of_bounds_default():
    with pytest.raises(
        ValueError, match=r"Default value for switch X must be True or False\.",
    ):
        Switch("X", 2)
