from flask_pancake import Flag, Sample, Switch
from flask_pancake.registry import registry


def test_registry():
    assert registry.flags("pancake") == {}
    assert registry.flags("ext") == {}
    assert registry.samples("pancake") == {}
    assert registry.samples("ext") == {}
    assert registry.switches("pancake") == {}
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

    assert registry.flags("pancake") == {"Flag1": flag1, "Flag2": flag2}
    assert registry.flags("ext") == {"Flag3": flag3}
    assert registry.samples("pancake") == {"Sample1": sample1, "Sample2": sample2}
    assert registry.samples("ext") == {"Sample3": sample3}
    assert registry.switches("pancake") == {"Switch1": switch1, "Switch2": switch2}
    assert registry.switches("ext") == {"Switch3": switch3}
