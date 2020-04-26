import pytest
from flask import Flask

from flask_pancake import Flag, FlaskPancake, Sample, Switch
from flask_pancake.constants import EXTENSION_NAME


def test_late_init():
    app = Flask(__name__)
    pancake = FlaskPancake()
    omlet = FlaskPancake(name="omlet")
    assert EXTENSION_NAME not in app.extensions
    assert "omlet" not in app.extensions
    pancake.init_app(app)
    omlet.init_app(app)
    assert EXTENSION_NAME in app.extensions
    assert "omlet" in app.extensions


def func1():
    pass  # pragma: no cover


def func2():
    pass  # pragma: no cover


@pytest.mark.parametrize(
    "funcs, expected",
    [
        ({"a": "tests.test_extension:func1"}, {"a": func1}),
        (
            {"a": "tests.test_extension:func1", "b": "tests.test_extension:func2"},
            {"a": func1, "b": func2},
        ),
        (
            {"b": "tests.test_extension:func2", "a": "tests.test_extension:func1"},
            {"b": func2, "a": func1},
        ),
    ],
)
def test_get_user_id_func(funcs, expected):
    pancake = FlaskPancake(group_funcs=funcs)
    assert pancake.group_funcs == expected


def test_flags_samples_switches():
    pancake = FlaskPancake()
    omlet = FlaskPancake(name="omlet")

    assert pancake.flags == {}
    assert omlet.flags == {}
    assert pancake.samples == {}
    assert omlet.samples == {}
    assert pancake.switches == {}
    assert omlet.switches == {}

    flag1 = Flag("Flag1", False)
    flag2 = Flag("Flag2", False, "omlet")

    sample1 = Sample("Sample1", 42)
    sample2 = Sample("Sample2", 42, "omlet")

    switch1 = Switch("Switch1", False)
    switch2 = Switch("Switch2", False, "omlet")

    assert pancake.flags == {"Flag1": flag1}
    assert omlet.flags == {"Flag2": flag2}
    assert pancake.samples == {"Sample1": sample1}
    assert omlet.samples == {"Sample2": sample2}
    assert pancake.switches == {"Switch1": switch1}
    assert omlet.switches == {"Switch2": switch2}
