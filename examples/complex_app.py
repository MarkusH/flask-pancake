from typing import List

from flask import Flask, abort, g, request, url_for
from flask_redis import FlaskRedis

from flask_pancake import Flag, FlaskPancake, Sample, Switch, blueprint
from flask_pancake.extension import GroupFunc

app = Flask(__name__)
app.secret_key = "s3cr!t"


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
pancake = FlaskPancake(app, name="other-flags")
redis = FlaskRedis(app)

FLAG_FOO_CAN_DO = Flag("FOO_CAN_DO", default=False)
FLAG_DO_SOMETHING_ELSE = Flag("DO_SOMETHING_ELSE", default=True)
SAMPLE_MY_ODDS = Sample("MY_ODDS", default=42)
SWITCH_ON_OR_OFF = Switch("ON_OR_OFF", default=True)
OTHER_SAMPLE = Sample("OTHER_SAMPLE", 1.2, "other-flags")


@app.before_first_request
def setup():
    FLAG_FOO_CAN_DO.enable_group("admin", object_id="yes")
    FLAG_FOO_CAN_DO.disable_group("admin", object_id="no")
    SAMPLE_MY_ODDS.set(13)
    SWITCH_ON_OR_OFF.disable()


@app.route("/")
def index():
    overview_url = url_for("pancake.overview")
    overview_url_other = url_for("pancake.overview", pancake="other-flags")
    status_url = url_for("pancake.status")
    status_url_other = url_for("pancake.status", pancake="other-flags")
    return (
        f'Check out <a href="{overview_url}?key=secret">a list of all feature flags</a>'
        f' and <a href="{status_url}">your current status</a> in one FlaskPancake '
        f'extension. And <a href="{overview_url_other}?key=secret">this overview page'
        f'</a> and <a href="{status_url_other}">this status page</a> for the second '
        "installed plugin.",
        200,
    )
