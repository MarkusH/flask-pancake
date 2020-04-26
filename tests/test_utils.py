from __future__ import annotations

import pytest

from flask_pancake.utils import import_from_string


def some_func() -> int:
    return 123  # pragma: no cover


def test_import_from_string_attr():
    func = import_from_string("tests.test_utils:some_func")
    assert func is some_func


def test_import_from_string_attr_not_found():
    with pytest.raises(AttributeError):
        assert import_from_string("tests.test_utils:DOES_NOT_EXIST")


def test_import_from_string_invalid_format():
    msg = (
        "Invalid function reference 'tests.test_utils'. The "
        "format is `path.to.module:function`"
    )
    with pytest.raises(ValueError, match=msg):
        import_from_string("tests.test_utils")
