import pytest
from flask import Flask

from flask_pancake import Flag, FlaskPancake, GroupFunc, Sample, Switch
from flask_pancake.constants import EXTENSION_NAME
from flask_pancake.extension import FunctionGroupFunc


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


class MyGroupFunc(GroupFunc):
    def __init__(self):
        self._counter = 0

    def __call__(self):
        ret = self._counter
        self._counter = (self._counter + 1) % 3
        return str(ret)

    def get_candidate_ids(self):
        return []  # pragma: no cover


@pytest.mark.parametrize(
    "funcs, expected",
    [
        ({"a": "tests.test_extension:func1"}, {"a": FunctionGroupFunc(func1)}),
        (
            {"a": "tests.test_extension:func1", "b": "tests.test_extension:func2"},
            {"a": FunctionGroupFunc(func1), "b": FunctionGroupFunc(func2)},
        ),
        (
            {"b": "tests.test_extension:func2", "a": "tests.test_extension:func1"},
            {"b": FunctionGroupFunc(func2), "a": FunctionGroupFunc(func1)},
        ),
    ],
)
def test_group_funcs_resolving(funcs, expected):
    pancake = FlaskPancake(group_funcs=funcs)
    assert pancake.group_funcs
    assert pancake.group_funcs == expected


def test_group_funcs_resolving_class():
    pancake = FlaskPancake(group_funcs={"a": "tests.test_extension:MyGroupFunc"})
    func = pancake.group_funcs["a"]
    assert isinstance(func, MyGroupFunc)
    assert [func(), func(), func(), func()] == ["0", "1", "2", "0"]


def test_group_funcs_resolving_fail():
    pancake = FlaskPancake(group_funcs={"a": object()})
    with pytest.raises(
        ValueError, match=r"Invalid group function <object object at .*> for 'a'\."
    ):
        pancake.group_funcs


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


def test_function_group_func():
    vals = ["1", "2", "3", "4"]
    ret_vals = iter(vals)

    def f():
        return next(ret_vals)

    fgf = FunctionGroupFunc(f)
    assert [fgf(), fgf(), fgf(), fgf()] == vals
    assert fgf.get_candidate_ids() == []

    f.get_candidate_ids = lambda: vals
    assert fgf.get_candidate_ids() == vals
