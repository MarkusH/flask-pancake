from flask_pancake import Flag, GroupFunc, Sample, Switch, blueprint
from flask_pancake.constants import EXTENSION_NAME
from flask_pancake.views import aggregate_data


def noop():
    return None  # pragma: no cover


def test_aggregate_data_empty(app):
    assert aggregate_data(app.extensions[EXTENSION_NAME]) == {
        "flags": [],
        "group_ids": [],
        "name": "pancake",
        "samples": [],
        "switches": [],
    }


def test_aggregate_data(app):
    Flag("Flag1", default=False)
    Flag("Flag2", default=True)
    flag3 = Flag("Flag3", default=False)
    flag3.enable()
    Sample("Sample1", default=12)
    sample2 = Sample("Sample2", default=24)
    sample2.set(48)
    Switch("Switch1", default=False)
    Switch("Switch2", default=True)
    switch3 = Switch("Switch3", default=False)
    switch3.enable()

    assert aggregate_data(app.extensions[EXTENSION_NAME]) == {
        "flags": [
            {"default": False, "groups": {}, "is_active": False, "name": "Flag1"},
            {"default": True, "groups": {}, "is_active": True, "name": "Flag2"},
            {"default": False, "groups": {}, "is_active": True, "name": "Flag3"},
        ],
        "group_ids": [],
        "name": "pancake",
        "samples": [
            {"default": 12, "name": "Sample1", "value": 12.0},
            {"default": 24, "name": "Sample2", "value": 48.0},
        ],
        "switches": [
            {"default": False, "is_active": False, "name": "Switch1"},
            {"default": True, "is_active": True, "name": "Switch2"},
            {"default": False, "is_active": True, "name": "Switch3"},
        ],
    }


def test_aggregate_data_groups(app):
    class IsAdmin(GroupFunc):
        def __call__(self):
            return None  # pragma: no cover

        def get_candidate_ids(self):
            return ["yes", "no"]

    ext = app.extensions[EXTENSION_NAME]
    ext._group_funcs = {"user": noop, "admin": IsAdmin}
    flag1 = Flag("Flag1", default=False)
    flag2 = Flag("Flag2", default=True)
    flag3 = Flag("Flag3", default=False)
    flag1.enable_group("user", object_id="uid1")
    flag1.disable_group("admin", object_id="yes")
    flag2.enable_group("admin", object_id="no")
    flag3.enable()

    assert aggregate_data(ext) == {
        "name": "pancake",
        "group_ids": ["user", "admin"],
        "flags": [
            {
                "name": "Flag1",
                "default": False,
                "is_active": False,
                "groups": {"user": {}, "admin": {"yes": False, "no": None}},
            },
            {
                "name": "Flag2",
                "default": True,
                "is_active": True,
                "groups": {"user": {}, "admin": {"yes": None, "no": True}},
            },
            {
                "name": "Flag3",
                "default": False,
                "is_active": True,
                "groups": {"user": {}, "admin": {"yes": None, "no": None}},
            },
        ],
        "samples": [],
        "switches": [],
    }


def test_view(app):
    class IsAdmin(GroupFunc):
        def __call__(self):
            return None  # pragma: no cover

        def get_candidate_ids(self):
            return ["yes", "no"]

    ext = app.extensions[EXTENSION_NAME]
    ext._group_funcs = {"user": noop, "admin": IsAdmin}
    flag1 = Flag("Flag1", default=False)
    flag2 = Flag("Flag2", default=True)
    flag3 = Flag("Flag3", default=False)
    flag1.enable_group("user", object_id="uid1")
    flag1.disable_group("admin", object_id="yes")
    flag2.enable_group("admin", object_id="no")
    flag3.enable()
    Sample("Sample1", default=12)
    sample2 = Sample("Sample2", default=24)
    sample2.set(48)
    Switch("Switch1", default=False)
    Switch("Switch2", default=True)
    switch3 = Switch("Switch3", default=False)
    switch3.enable()

    app.register_blueprint(blueprint, url_prefix="/p")
    with app.test_client() as client:
        resp = client.get("/p/")
        assert resp.status_code == 200
        assert resp.data.decode() == (
            "<h1>Flask Pancake</h1>\n"
            "Extension: pancake\n"
            "\n"
            "<h2>Flags</h2>\n"
            '<table border="1">\n'
            "  <thead>\n"
            "    <th>Name</th>\n"
            "    <th>Default</th>\n"
            "    <th>Is active globally</th><th>Is active for <em>user</em></th><th>Is active for <em>admin</em></th></thead><tr>\n"  # noqa
            "    <td>Flag1</td>\n"
            "    <td>False</td>\n"
            "    <td>False</td><td>No candidates available</td><td><p>yes: False</p><p>no: None</p></td></tr><tr>\n"  # noqa
            "    <td>Flag2</td>\n"
            "    <td>True</td>\n"
            "    <td>True</td><td>No candidates available</td><td><p>yes: None</p><p>no: True</p></td></tr><tr>\n"  # noqa
            "    <td>Flag3</td>\n"
            "    <td>False</td>\n"
            "    <td>True</td><td>No candidates available</td><td><p>yes: None</p><p>no: None</p></td></tr></table>\n"  # noqa
            "\n"
            "<h2>Samples</h2>\n"
            '<table border="1">\n'
            "  <thead>\n"
            "    <th>Name</th>\n"
            "    <th>Default</th>\n"
            "    <th>Value</th>\n"
            "  </thead><tr>\n"
            "    <td>Sample1</td>\n"
            "    <td>12</td>\n"
            "    <td>12.0</td>\n"
            "  </tr><tr>\n"
            "    <td>Sample2</td>\n"
            "    <td>24</td>\n"
            "    <td>48.0</td>\n"
            "  </tr></table>\n"
            "\n"
            "<h2>Switches</h2>\n"
            '<table border="1">\n'
            "  <thead>\n"
            "    <th>Name</th>\n"
            "    <th>Default</th>\n"
            "    <th>Is Active</th>\n"
            "  </thead><tr>\n"
            "    <td>Switch1</td>\n"
            "    <td>False</td>\n"
            "    <td>False</td>\n"
            "  </tr><tr>\n"
            "    <td>Switch2</td>\n"
            "    <td>True</td>\n"
            "    <td>True</td>\n"
            "  </tr><tr>\n"
            "    <td>Switch3</td>\n"
            "    <td>False</td>\n"
            "    <td>True</td>\n"
            "  </tr></table>"
        )

        resp = client.get("/p/", content_type="application/json")
        assert resp.status_code == 200
        assert resp.json == {
            "flags": [
                {
                    "default": False,
                    "groups": {"admin": {"no": None, "yes": False}, "user": {}},
                    "is_active": False,
                    "name": "Flag1",
                },
                {
                    "default": True,
                    "groups": {"admin": {"no": True, "yes": None}, "user": {}},
                    "is_active": True,
                    "name": "Flag2",
                },
                {
                    "default": False,
                    "groups": {"admin": {"no": None, "yes": None}, "user": {}},
                    "is_active": True,
                    "name": "Flag3",
                },
            ],
            "group_ids": ["user", "admin"],
            "name": "pancake",
            "samples": [
                {"default": 12, "name": "Sample1", "value": 12.0},
                {"default": 24, "name": "Sample2", "value": 48.0},
            ],
            "switches": [
                {"default": False, "is_active": False, "name": "Switch1"},
                {"default": True, "is_active": True, "name": "Switch2"},
                {"default": False, "is_active": True, "name": "Switch3"},
            ],
        }


def test_view_ext_not_found(app):
    app.register_blueprint(blueprint, url_prefix="/p")
    with app.test_client() as client:
        resp = client.get("/p/foo")
        assert resp.status_code == 404
