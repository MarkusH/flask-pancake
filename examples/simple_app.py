from flask import Flask
from flask_redis import FlaskRedis

from flask_pancake import FlaskPancake, Switch, blueprint

app = Flask(__name__)
app.secret_key = "s3cr!t"
app.register_blueprint(blueprint, url_prefix="/pancakes")
pancake = FlaskPancake(app)
redis = FlaskRedis(app)

SWITCH_ON_OR_OFF = Switch("ON_OR_OFF", default=False)


@app.route("/")
def index():
    if SWITCH_ON_OR_OFF.is_active():
        return (
            "Hello World!<br>It worked!<br>Now, try to set the key "
            "<code>SWITCH:pancake:ON_OR_OFF</code> back to <code>0</code> or "
            "delete the key in Redis with <code>del SWITCH:pancake:ON_OR_OFF</code>. "
            "Then refresh the page again.",
            200,
        )
    else:
        return (
            "Not found<br>Try setting the key <code>SWITCH:pancake:ON_OR_OFF</code> in "
            "Redis to <code>1</code> using <code>set SWITCH:pancake:ON_OR_OFF 1</code>."
            "<br>Refresh the page afterwards.",
            404,
        )
