from dataclasses import dataclass
from typing import Optional

import pytest
from flask import Flask, request
from flask_redis import FlaskRedis

from flask_pancake import FlaskPancake
from flask_pancake.flags import Flag
from flask_pancake.registry import registry


@dataclass
class Group:
    id: str
    name: str


@dataclass
class User:
    id: str
    name: str
    superuser: bool
    group: Optional[Group] = None


@pytest.fixture
def e2e_setup():
    app = Flask(__name__)
    app.config["TESTING"] = True
    FlaskRedis(app)

    CAN_DO = Flag("CAN_DO", False)
    context = {"current_user": None}

    @app.route("/")
    def view():
        if CAN_DO.is_active():
            return "yes", 200
        return "no", 404

    @app.before_request
    def auth_user():
        request.user = context["current_user"]

    def get_user_id():
        return getattr(getattr(request, "user", None), "id", None)

    def get_superuser():
        return getattr(getattr(request, "user", None), "superuser", None) and "y" or "n"

    def get_group_id():
        return getattr(
            getattr(getattr(request, "user", None), "group", None), "id", None
        )

    FlaskPancake(
        app,
        group_funcs={
            "user": get_user_id,
            "superuser": get_superuser,
            "group": get_group_id,
        },
    )
    with app.app_context():
        app.extensions["redis"].flushall()
        registry.__clear__()
        yield app, context, CAN_DO
        app.extensions["redis"].flushall()
        registry.__clear__()


def test_flags_unauthenticated(e2e_setup):
    app, context, CAN_DO = e2e_setup

    with app.test_client() as client:
        resp = client.get("/")

    assert resp.status_code == 404
    assert resp.data == b"no"


def test_flags_superuser(e2e_setup):
    app, context, CAN_DO = e2e_setup

    CAN_DO.enable_group("superuser", object_id="y")
    context["current_user"] = User(id="1", name="Jane Doe", superuser=True)

    with app.test_client() as client:
        resp = client.get("/")
    assert resp.status_code == 200
    assert resp.data == b"yes"


def test_flags_group(e2e_setup):
    app, context, CAN_DO = e2e_setup

    CAN_DO.enable_group("group", object_id="a")
    context["current_user"] = User(
        id="1", name="Jane Doe", superuser=True, group=Group(id="a", name="A")
    )

    with app.test_client() as client:
        resp = client.get("/")
    assert resp.status_code == 200
    assert resp.data == b"yes"


@pytest.mark.parametrize(
    "user_id, superuser, group_id, success",
    [
        ("1", False, None, True),
        ("2", False, None, False),
        ("2", True, None, True),
        ("2", False, "admins", True),
        ("2", False, "members", False),
        ("3", True, "admins", False),
    ],
)
def test_multi_users_superusers_groups(
    user_id, superuser, group_id, success, e2e_setup
):
    app, context, CAN_DO = e2e_setup

    CAN_DO.enable_group("user", object_id="1")
    CAN_DO.disable_group("user", object_id="3")
    CAN_DO.enable_group("superuser", object_id="y")
    CAN_DO.enable_group("group", object_id="admins")

    context["current_user"] = User(
        id=user_id,
        name="Jane Doe",
        superuser=superuser,
        group=Group(id=group_id, name="G") if group_id else None,
    )

    with app.test_client() as client:
        resp = client.get("/")

    if success:
        assert resp.status_code == 200
        assert resp.data == b"yes"
    else:
        assert resp.status_code == 404
        assert resp.data == b"no"
