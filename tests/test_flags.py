from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from flask_pancake import Flag, FlaskPancake
from flask_pancake.constants import EXTENSION_NAME, RAW_FALSE, RAW_TRUE

if TYPE_CHECKING:
    from flask import Flask


def test_flag(app: Flask):
    uid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME].get_user_id_func = lambda: uid

    off = Flag("default_off", False)
    on = Flag("default_on", True)

    assert app.extensions["redis"].get("FLAG:DEFAULT_OFF") is None
    assert app.extensions["redis"].get("FLAG:DEFAULT_ON") is None

    assert off.is_active() is False
    assert on.is_active() is True

    assert app.extensions["redis"].get("FLAG:DEFAULT_OFF") == RAW_FALSE
    assert app.extensions["redis"].get("FLAG:DEFAULT_ON") == RAW_TRUE

    off.enable()
    on.disable()

    assert app.extensions["redis"].get("FLAG:DEFAULT_OFF") == RAW_TRUE
    assert app.extensions["redis"].get("FLAG:DEFAULT_ON") == RAW_FALSE

    assert off.is_active() is True
    assert on.is_active() is False


def test_flag_user(app: Flask):
    uid1 = str(uuid.uuid4())
    uid2 = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME].get_user_id_func = lambda: uid1

    feature = Flag("FEATURE", False)

    assert app.extensions["redis"].get("FLAG:FEATURE") is None

    assert feature.is_active() is False
    feature.enable_user()
    assert feature.is_active() is True

    assert app.extensions["redis"].get("FLAG:FEATURE") == RAW_FALSE
    assert app.extensions["redis"].get(f"FLAG:FEATURE:user:{uid1}") == RAW_TRUE

    app.extensions[EXTENSION_NAME].get_user_id_func = lambda: uid2
    assert feature.is_active() is False

    feature.enable()
    assert app.extensions["redis"].get("FLAG:FEATURE") == RAW_TRUE

    assert feature.is_active() is True

    feature.disable_user()

    assert feature.is_active() is False
    assert app.extensions["redis"].get(f"FLAG:FEATURE:user:{uid2}") == RAW_FALSE

    feature.clear()
    assert app.extensions["redis"].get("SAMPLE:FEATURE") is None


def test_key(app: Flask):
    flag = Flag("my-flag", True)
    app.extensions[EXTENSION_NAME].get_user_id_func = lambda: "some-uid"
    assert flag.key == "FLAG:MY-FLAG"
    assert flag.user_key == "FLAG:MY-FLAG:user:some-uid"


def test_scoped_key(app: Flask):
    FlaskPancake(app, name="scopy")
    flag = Flag("my-flag", True, extension="scopy")
    app.extensions[EXTENSION_NAME].get_user_id_func = lambda: "some-uid"
    app.extensions["scopy"].get_user_id_func = lambda: "scopy-uid"
    assert flag.key == "FLAG:MY-FLAG:scopy"
    assert flag.user_key == "FLAG:MY-FLAG:scopy:user:scopy-uid"
