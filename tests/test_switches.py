from __future__ import annotations

from typing import TYPE_CHECKING

from flask_pancake import RAW_FALSE, RAW_TRUE, Switch

if TYPE_CHECKING:
    from flask import Flask


def test_switch(app: Flask):
    off = Switch("default_off", False)
    on = Switch("default_on", True)

    assert app.extensions["redis"].get("SWITCH:DEFAULT_OFF") is None
    assert app.extensions["redis"].get("SWITCH:DEFAULT_ON") is None

    assert off.is_active() is False
    assert on.is_active() is True

    assert app.extensions["redis"].get("SWITCH:DEFAULT_OFF") == RAW_FALSE
    assert app.extensions["redis"].get("SWITCH:DEFAULT_ON") == RAW_TRUE

    off.enable()
    on.disable()

    assert app.extensions["redis"].get("SWITCH:DEFAULT_OFF") == RAW_TRUE
    assert app.extensions["redis"].get("SWITCH:DEFAULT_ON") == RAW_FALSE

    assert off.is_active() is True
    assert on.is_active() is False

    off.clear()
    assert app.extensions["redis"].get("SWITCH:DEFAULT_OFF") is None
