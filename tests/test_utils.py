from __future__ import annotations

from unittest import mock

import pytest
from flask import Flask, g, jsonify, request
from itsdangerous import BadData

from flask_pancake import FlaskPancake, Sample
from flask_pancake.utils import (
    decode_sample_state,
    encode_sample_state,
    import_from_string,
)


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


def test_encode_decode_sample_state(app: Flask):
    app.secret_key = "s3cr!t"
    d = {"foo": True, "bar": False}
    assert decode_sample_state(encode_sample_state(d)) == d
    assert decode_sample_state(encode_sample_state(d)) is not d


def test_encode_decode_sample_state_require_secret_key(app: Flask):
    msg = r"Cannot load sample flags cookie since app\.SECRET_KEY is not set\."
    with pytest.raises(RuntimeError, match=msg):
        decode_sample_state("")
    msg = r"Cannot store sample flags cookie since app\.SECRET_KEY is not set\."
    with pytest.raises(RuntimeError, match=msg):
        encode_sample_state("")


def test_load_store_cookie(app: Flask):
    app.secret_key = "s3cr!t"
    FlaskPancake(app, name="other")
    sample1 = Sample("s1", 42)
    sample2 = Sample("s2", 13, "other")

    @app.route("/")
    def view():
        return jsonify(
            {
                "cookies": request.cookies,
                "request_state": g.get("pancakes"),
                "sample1": sample1.is_active(),
                "sample2": sample2.is_active(),
            }
        )

    with app.test_client() as client:
        with mock.patch("random.uniform", return_value=41.999):
            resp = client.get("/")
            assert resp.json == {
                "cookies": {},
                "request_state": None,
                "sample1": True,
                "sample2": False,
            }
        g.pop("pancakes")
        with mock.patch("random.uniform", return_value=12.99):
            resp = client.get("/")
            assert resp.json == {
                "cookies": {
                    "other": "eyJzMiI6ZmFsc2V9.MUaGnFYuUZPDFdQOTsK--NNHX-w",
                    "pancake": "eyJzMSI6dHJ1ZX0.dOXBnEqzY3GMDtreJMU-BRduDq8",
                },
                "request_state": {"other": {"s2": False}, "pancake": {"s1": True}},
                "sample1": True,
                "sample2": False,
            }
        g.pop("pancakes")
        with mock.patch("random.uniform", return_value=12.99):
            with mock.patch(
                "flask_pancake.utils.decode_sample_state", side_effect=BadData("fail")
            ):
                resp = client.get("/")
                assert resp.json == {
                    "cookies": {
                        "other": "eyJzMiI6ZmFsc2V9.MUaGnFYuUZPDFdQOTsK--NNHX-w",
                        "pancake": "eyJzMSI6dHJ1ZX0.dOXBnEqzY3GMDtreJMU-BRduDq8",
                    },
                    "request_state": None,
                    "sample1": True,
                    "sample2": True,
                }
