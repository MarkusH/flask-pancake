from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest

from flask_pancake import Flag
from flask_pancake.constants import EXTENSION_NAME, RAW_FALSE, RAW_TRUE

if TYPE_CHECKING:
    from flask import Flask


def test_flag(app: Flask):
    uid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: uid}

    off = Flag("default_off", False)
    on = Flag("default_on", True)

    assert app.extensions["redis"].get("FLAG:pancake:DEFAULT_OFF") is None
    assert app.extensions["redis"].get("FLAG:pancake:DEFAULT_ON") is None

    assert off.is_active() is False
    assert on.is_active() is True

    assert app.extensions["redis"].get("FLAG:pancake:DEFAULT_OFF") == RAW_FALSE
    assert app.extensions["redis"].get("FLAG:pancake:DEFAULT_ON") == RAW_TRUE

    off.enable()
    on.disable()

    assert app.extensions["redis"].get("FLAG:pancake:DEFAULT_OFF") == RAW_TRUE
    assert app.extensions["redis"].get("FLAG:pancake:DEFAULT_ON") == RAW_FALSE

    assert off.is_active() is True
    assert on.is_active() is False


def test_clear(app):
    feature = Flag("FEATURE", True)
    key = "FLAG:pancake:FEATURE"

    assert app.extensions["redis"].get(key) is None
    feature.disable()
    assert app.extensions["redis"].get(key) == RAW_FALSE
    feature.clear()
    assert app.extensions["redis"].get(key) is None


def test_disable(app):
    feature = Flag("FEATURE", True)
    key = "FLAG:pancake:FEATURE"

    assert app.extensions["redis"].get(key) is None
    assert feature.is_active() is True

    feature.disable()

    assert app.extensions["redis"].get(key) == RAW_FALSE
    assert feature.is_active() is False


def test_enable(app):
    feature = Flag("FEATURE", False)
    key = "FLAG:pancake:FEATURE"

    assert app.extensions["redis"].get(key) is None
    assert feature.is_active() is False

    feature.enable()

    assert app.extensions["redis"].get(key) == RAW_TRUE
    assert feature.is_active() is True


def test_clear_group(app):
    uid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: uid}
    feature = Flag("FEATURE", True)
    object_key = f"FLAG:pancake:k:user:FEATURE:{uid}"
    tracking_key = "FLAG:pancake:t:user:FEATURE"

    assert app.extensions["redis"].get(object_key) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()

    feature.disable_group("user")

    assert app.extensions["redis"].get(object_key) == RAW_FALSE
    assert app.extensions["redis"].smembers(tracking_key) == {object_key.encode()}

    feature.clear_group("user")

    assert app.extensions["redis"].get(object_key) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()


def test_clear_group_cannot_derive(app):
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: None}
    feature = Flag("FEATURE", True)

    with pytest.raises(RuntimeError, match="Cannot derive identifier for group 'user'"):
        feature.clear_group("user")


def test_clear_all_group(app):
    uid1 = str(uuid.uuid4())
    uid2 = str(uuid.uuid4())
    context = {}
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: context["uid"]}
    feature = Flag("FEATURE", False)
    object_key1 = f"FLAG:pancake:k:user:FEATURE:{uid1}"
    object_key2 = f"FLAG:pancake:k:user:FEATURE:{uid2}"
    tracking_key = "FLAG:pancake:t:user:FEATURE"

    assert app.extensions["redis"].smembers(tracking_key) == set()
    feature.clear_all_group("user")

    context["uid"] = uid1
    feature.enable_group("user")

    context["uid"] = uid2
    feature.enable_group("user")

    assert app.extensions["redis"].get(object_key1) == RAW_TRUE
    assert app.extensions["redis"].get(object_key2) == RAW_TRUE
    assert app.extensions["redis"].smembers(tracking_key) == {
        object_key1.encode(),
        object_key2.encode(),
    }

    feature.clear_all_group("user")

    assert app.extensions["redis"].get(object_key1) is None
    assert app.extensions["redis"].get(object_key2) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()


def test_disable_group(app):
    uid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: uid}
    feature = Flag("FEATURE", True)
    object_key = f"FLAG:pancake:k:user:FEATURE:{uid}"
    tracking_key = "FLAG:pancake:t:user:FEATURE"

    assert app.extensions["redis"].get(object_key) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()
    assert feature.is_active() is True

    feature.disable_group("user")

    assert app.extensions["redis"].get(object_key) == RAW_FALSE
    assert app.extensions["redis"].smembers(tracking_key) == {object_key.encode()}
    assert feature.is_active() is False


def test_disable_group_cannot_derive(app):
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: None}
    feature = Flag("FEATURE", True)

    with pytest.raises(RuntimeError, match="Cannot derive identifier for group 'user'"):
        feature.disable_group("user")


def test_enable_group(app):
    uid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: uid}
    feature = Flag("FEATURE", False)
    object_key = f"FLAG:pancake:k:user:FEATURE:{uid}"
    tracking_key = "FLAG:pancake:t:user:FEATURE"

    assert app.extensions["redis"].get(object_key) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()
    assert feature.is_active() is False

    feature.enable_group("user")

    assert app.extensions["redis"].get(object_key) == RAW_TRUE
    assert app.extensions["redis"].smembers(tracking_key) == {object_key.encode()}
    assert feature.is_active() is True


def test_enable_group_cannot_derive(app):
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: None}
    feature = Flag("FEATURE", True)

    with pytest.raises(RuntimeError, match="Cannot derive identifier for group 'user'"):
        feature.enable_group("user")


def test_clear_disable_enable_group_object_id(app):
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": None}
    feature = Flag("FEATURE", True)
    object_key1 = "FLAG:pancake:k:user:FEATURE:1"
    object_key2 = "FLAG:pancake:k:user:FEATURE:2"
    tracking_key = "FLAG:pancake:t:user:FEATURE"

    assert app.extensions["redis"].get(object_key1) is None
    assert app.extensions["redis"].get(object_key2) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()

    feature.enable_group("user", object_id="1")
    feature.enable_group("user", object_id="2")

    assert app.extensions["redis"].get(object_key1) == RAW_TRUE
    assert app.extensions["redis"].get(object_key2) == RAW_TRUE
    assert app.extensions["redis"].smembers(tracking_key) == {
        object_key1.encode(),
        object_key2.encode(),
    }

    feature.disable_group("user", object_id="1")
    feature.disable_group("user", object_id="2")

    assert app.extensions["redis"].get(object_key1) == RAW_FALSE
    assert app.extensions["redis"].get(object_key2) == RAW_FALSE
    assert app.extensions["redis"].smembers(tracking_key) == {
        object_key1.encode(),
        object_key2.encode(),
    }

    feature.clear_group("user", object_id="1")
    feature.clear_group("user", object_id="2")

    assert app.extensions["redis"].get(object_key1) is None
    assert app.extensions["redis"].get(object_key2) is None
    assert app.extensions["redis"].smembers(tracking_key) == set()


@pytest.mark.parametrize(
    "default, group, user, expected",
    [
        #
        (False, None, None, False),
        (True, None, None, True),
        #
        (False, False, None, False),
        (True, False, None, False),
        #
        (False, True, None, True),
        (True, True, None, True),
        #
        (False, None, False, False),
        (True, None, False, False),
        #
        (False, False, False, False),
        (True, False, False, False),
        #
        (False, True, False, False),
        (True, True, False, False),
        #
        (False, None, True, True),
        (True, None, True, True),
        #
        (False, False, True, True),
        (True, False, True, True),
        #
        (False, True, True, True),
        (True, True, True, True),
    ],
)
def test_flag_multiple_groups(default, group, user, expected, app: Flask):
    uid = str(uuid.uuid4())
    gid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {
        "user": lambda: uid,
        "group": lambda: gid,
    }

    feature = Flag("FEATURE", default)

    if group is True:
        feature.enable_group("group")
    elif group is False:
        feature.disable_group("group")

    if user is True:
        feature.enable_group("user")
    elif user is False:
        feature.disable_group("user")

    assert feature.is_active() is expected


def test_flag_multiple_groups_fallback(app: Flask):
    gid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {
        "user": lambda: None,
        "group": lambda: gid,
    }

    feature = Flag("FEATURE", False)
    feature.enable_group("group")
    assert feature.is_active() is True


def test_out_of_bounds_default():
    with pytest.raises(
        ValueError, match=r"Default value for flag X must be True or False\.",
    ):
        Flag("X", -1)


def test_get_group_keys_no_groups(app: Flask):
    feature = Flag("FEATURE", False)
    msg = (
        "No group_funcs defined on FlaskPancake extension 'pancake'. "
        "If you don't have users or other types of groups in your application "
        "and want a global flag to turn things on and off, use a `Switch` "
        "instead."
    )
    with pytest.raises(RuntimeError, match=msg):
        feature._get_group_keys("user")


def test_get_group_keys_group_not_defined(app: Flask):
    app.extensions[EXTENSION_NAME]._group_funcs = {"group": None}
    feature = Flag("FEATURE", False)
    msg = (
        "Invalid group identifer 'user'. This group doesn't seem to be "
        "registered in the FlaskPancake extension 'pancake'."
    )
    with pytest.raises(RuntimeError, match=msg):
        feature._get_group_keys("user")
