import uuid
from unittest import mock

from flask import Flask, g

from flask_pancake import Flag, Sample, Switch
from flask_pancake.commands import (
    flag_clear,
    flag_clear_group,
    flag_disable,
    flag_disable_group,
    flag_enable,
    flag_enable_group,
    flag_list,
    flag_list_group,
    sample_clear,
    sample_list,
    sample_set,
    switch_clear,
    switch_disable,
    switch_enable,
    switch_list,
)
from flask_pancake.constants import EXTENSION_NAME


def test_flags(app: Flask):
    runner = app.test_cli_runner()
    feature = Flag("FEATURE", default=False)

    result = runner.invoke(flag_enable, ["FEATURE"])
    assert feature.is_active() is True
    assert "Flag 'FEATURE' enabled." in result.output

    result = runner.invoke(flag_disable, args=["FEATURE"])
    assert feature.is_active() is False
    assert "Flag 'FEATURE' disabled." in result.output

    feature.enable()
    assert feature.is_active() is True

    result = runner.invoke(flag_clear, args=["FEATURE"])
    assert feature.is_active() is False
    assert "Flag 'FEATURE' cleared." in result.output


def test_flags_group(app: Flask):
    runner = app.test_cli_runner()
    feature = Flag("FEATURE", default=False)
    uid = str(uuid.uuid4())
    app.extensions[EXTENSION_NAME]._group_funcs = {"user": lambda: uid}

    result = runner.invoke(flag_enable_group, ["FEATURE", "user", uid])
    assert feature.is_active() is True
    assert (
        f"Object '{uid}' in group 'user' for flag 'FEATURE' enabled." in result.output
    )

    result = runner.invoke(flag_list_group, ["user", uid])
    assert result.output == "FEATURE: Yes (default: No)\n"

    result = runner.invoke(flag_disable_group, args=["FEATURE", "user", uid])
    assert feature.is_active() is False
    assert (
        f"Object '{uid}' in group 'user' for flag 'FEATURE' disabled." in result.output
    )

    feature.enable_group("user", object_id=uid)
    assert feature.is_active() is True

    result = runner.invoke(flag_clear_group, args=["FEATURE", "user", uid])
    assert feature.is_active() is False
    assert (
        f"Object '{uid}' in group 'user' for flag 'FEATURE' cleared." in result.output
    )

    result = runner.invoke(flag_list_group, ["user", uid])
    assert result.output == "FEATURE: N/A (default: No)\n"


def test_flag_list(app: Flask):
    runner = app.test_cli_runner()
    Flag("FEATURE1", default=False)
    Flag("FEATURE3", default=True)
    Flag("FEATURE2", default=False)

    result = runner.invoke(flag_list)
    assert result.output == (
        "FEATURE1: No (default: No)\n"
        "FEATURE2: No (default: No)\n"
        "FEATURE3: Yes (default: Yes)\n"
    )


def test_sample(app: Flask):
    runner = app.test_cli_runner()
    sample = Sample("SAMPLE", default=0)

    with mock.patch("random.uniform", return_value=41.999):
        assert sample.is_active() is False

    result = runner.invoke(sample_set, ["SAMPLE", "42"])
    assert "Sample 'SAMPLE' set to '42.0'." in result.output

    # Remove the tracked is_active state from `g`:
    g.pop("pancakes", None)

    with mock.patch("random.uniform", return_value=41):
        assert sample.is_active()

    # Remove the tracked is_active state from `g`:
    g.pop("pancakes", None)

    result = runner.invoke(sample_clear, args=["SAMPLE"])
    with mock.patch("random.uniform", return_value=41.999):
        assert sample.is_active() is False
    assert "Sample 'SAMPLE' cleared." in result.output

    result = runner.invoke(sample_set, ["SAMPLE", "101"])
    assert (
        "Invalid value for 'VALUE': Value for sample must be in the range [0, 100]."
        in result.output
    )


def test_sample_list(app: Flask):
    runner = app.test_cli_runner()
    Sample("SAMPLE1", default=1)
    Sample("SAMPLE3", default=2)
    Sample("SAMPLE2", default=3)

    result = runner.invoke(sample_list)
    assert result.output == (
        "SAMPLE1: 1.0 (default: 1)\n"
        "SAMPLE2: 3.0 (default: 3)\n"
        "SAMPLE3: 2.0 (default: 2)\n"
    )


def test_switch(app: Flask):
    runner = app.test_cli_runner()
    switch = Switch("SWITCH", default=False)

    result = runner.invoke(switch_enable, ["SWITCH"])
    assert switch.is_active() is True
    assert "Switch 'SWITCH' enabled." in result.output

    result = runner.invoke(switch_disable, args=["SWITCH"])
    assert switch.is_active() is False
    assert "Switch 'SWITCH' disabled." in result.output

    switch.enable()
    assert switch.is_active() is True

    result = runner.invoke(switch_clear, args=["SWITCH"])
    assert switch.is_active() is False
    assert "Switch 'SWITCH' cleared." in result.output


def test_switch_list(app: Flask):
    runner = app.test_cli_runner()
    Switch("SWITCH1", default=False)
    Switch("SWITCH3", default=True)
    Switch("SWITCH2", default=False)

    result = runner.invoke(switch_list)
    assert result.output == (
        "SWITCH1: No (default: No)\n"
        "SWITCH2: No (default: No)\n"
        "SWITCH3: Yes (default: Yes)\n"
    )
