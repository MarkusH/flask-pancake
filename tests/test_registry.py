import pytest

from flask_pancake import Flag, Sample, Switch
from flask_pancake.constants import EXTENSION_NAME
from flask_pancake.flags import AbstractFlag
from flask_pancake.registry import registry


def test_registry():
    assert registry.flags(EXTENSION_NAME) == {}
    assert registry.flags("ext") == {}
    assert registry.samples(EXTENSION_NAME) == {}
    assert registry.samples("ext") == {}
    assert registry.switches(EXTENSION_NAME) == {}
    assert registry.switches("ext") == {}

    flag1 = Flag("Flag1", False)
    flag2 = Flag("Flag2", False)
    flag3 = Flag("Flag3", False, "ext")

    sample1 = Sample("Sample1", 42)
    sample2 = Sample("Sample2", 42)
    sample3 = Sample("Sample3", 42, "ext")

    switch1 = Switch("Switch1", False)
    switch2 = Switch("Switch2", False)
    switch3 = Switch("Switch3", False, "ext")

    assert registry.flags(EXTENSION_NAME) == {"Flag1": flag1, "Flag2": flag2}
    assert registry.flags("ext") == {"Flag3": flag3}
    assert registry.samples(EXTENSION_NAME) == {"Sample1": sample1, "Sample2": sample2}
    assert registry.samples("ext") == {"Sample3": sample3}
    assert registry.switches(EXTENSION_NAME) == {"Switch1": switch1, "Switch2": switch2}
    assert registry.switches("ext") == {"Switch3": switch3}


def test_register_typerror():
    class MyFlag(AbstractFlag):
        def is_active(self):
            return False  # pragma: no cover

    with pytest.raises(TypeError, match="Cannot register class of type MyFlag"):
        MyFlag("abstract", False)
