from typing import List

from flask import Flask, abort, g, request, url_for
from flask_redis import FlaskRedis

from flask_pancake import Flag, FlaskPancake, Sample, Switch, blueprint
from flask_pancake.extension import GroupFunc

app = Flask(__name__)


@blueprint.before_request
def auth():
    if request.endpoint == "pancake.overview":
        if "key" in request.args:
            if request.args["key"] == "secret":
                return
            abort(403)
        abort(401)


app.register_blueprint(blueprint, url_prefix="/pancakes")


def user_id_func() -> str:
    return getattr(g, "user_id", None)


class IsAdmin(GroupFunc):
    def __call__(self) -> str:
        if getattr(g, "user_id", None) in {7, 42, 1337}:
            return "yes"
        return "no"

    def get_candidate_ids(self) -> List[str]:
        return ["yes", "no"]


pancake = FlaskPancake(app, group_funcs={"user": user_id_func, "admin": IsAdmin()})
redis = FlaskRedis(app)

FLAG_FOO_CAN_DO = Flag("FOO_CAN_DO", default=False)
FLAG_DO_SOMETHING_ELSE = Flag("DO_SOMETHING_ELSE", default=True)
SAMPLE_MY_ODDS = Sample("MY_ODDS", default=42)
SWITCH_ON_OR_OFF = Switch("ON_OR_OFF", default=True)


@app.before_first_request
def setup():
    FLAG_FOO_CAN_DO.enable_group("admin", object_id="yes")
    FLAG_FOO_CAN_DO.disable_group("admin", object_id="no")
    SAMPLE_MY_ODDS.set(13)
    SWITCH_ON_OR_OFF.disable()


@app.route("/")
def index():
    overview_url = url_for("pancake.overview")
    status_url = url_for("pancake.status")
    return (
        f'Check out <a href="{overview_url}?key=secret">a list of all feature flags</a>'
        f' and <a href="{status_url}">your current status</a>',
        200,
    )
