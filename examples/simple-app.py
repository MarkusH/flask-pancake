from flask import Flask
from flask_redis import FlaskRedis

from flask_pancake import FlaskPancake, Switch

app = Flask(__name__)
pancake = FlaskPancake(app)
redis = FlaskRedis(app)

SWITCH_FEATURE = Switch("FEATURE", default=False)


@app.route("/")
def index():
    if SWITCH_FEATURE.is_active():
        return (
            "Hello World!<br>It worked!<br>Now, try to set the key "
            "<code>SWITCH:FEATURE</code> back to <code>0</code> or delete the "
            "key in Redis with <code>del SWITCH:FEATURE</code>. "
            "Then refresh the page again.",
            200,
        )
    else:
        return (
            "Not found<br>Try setting the key <code>SWITCH:FEATURE</code> "
            "in Redis to <code>1</code> using <code>set SWITCH:FEATURE 1</code>. "
            "Refresh the page afterwards.",
            404,
        )
