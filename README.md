# flask-pancake

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/MarkusH/flask-pancake/CI/master?style=for-the-badge)
![Codecov branch](https://img.shields.io/codecov/c/gh/MarkusH/flask-pancake/master?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/flask-pancake?style=for-the-badge)

Feature Flagging for Flask

This library was heavily inspired by
[django-waffle](https://github.com/django-waffle/django-waffle).

## Installation

`flask-pancake` depends on [Redis](https://redis.io/) and the [flask-redis](https://pypi.org/project/flask-redis/) Python package.

```bash
$ python -m pip install flask-pancake
Successfully installed flask-pancake
```

```python
from flask import Flask
from flask_pancake import FlaskPancake, Switch
from flask_redis import FlaskRedis

app = Flask(__name__)
app.secret_key = "s3cr!t"
pancake = FlaskPancake(app)
redis = FlaskRedis(app)

SWITCH_FEATURE = Switch("FEATURE", default=False)


@app.route("/")
def index():
    if SWITCH_FEATURE.is_active():
        return "Hello World!", 200
    else:
        return "Not found", 404
```

Alternatively, if you use a `create_app()` method to configure your Flask app,
use `pancake.init_app()`:

```python
from flask import Flask
from flask_pancake import FlaskPancake

pancake = FlaskPancake()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "s3cr!t"
    pancake.init_app(app)
    return app
```

## Usage

`flask-pancake` provides three types of flags:

* `Switch`es, which are either globally active or inactive. A common use case
  for these are system-wide enabling or disabling of a feature. E.g. in the
  context of a dependency on a third party service, disabling a feature with a
  global switch when that service is unavailable.

* `Flag`s are like Switches but can be overridden for individual groups. To
  make use of `Flag`s, one needs to define at least one function that returns a
  group's unique ID or `None`. Groups can be anything that you want users to be
  grouped by: their user ID (which would allow per-user enabling/disabling of
  features), a user's attribute, such as "is_superuser" or "is_staff", or
  anything else that you can think of.

  The groups are tried in order. The first one to match will be used. Meaning,
  more specific functions should be defined first, less specific functions last.

  ```python
  from flask import request
  from flask_pancake import FlaskPancake

  def get_group_user():
      # If the `request` object has a `user` attribute and the `user` object
      # has a `uid` attribute, return that.
      return getattr(getattr(request, "user", None), "uid", None)

  def get_group_superuser():
      # If the `request` object has a `user` attribute and the `user` object
      # has an `is_superuser` attribute, return "y" if that is boolean `True`
      # or "n" if it isn't.
      return getattr(getattr(request, "user", None), "is_superuser", None) and "y" or "n"

  # Alternatively, instead of using `get_group_superuser()` one can use a
  # slightly more verbose class-based approach which has the added benefit
  # of adding additional value to the flask-pancake overview API view (see
  # below).
  class IsSuperuser(GroupFunc):
      def __call__(self) -> str:
          return getattr(getattr(request, "user", None), "is_superuser", None) and "y" or "n"

      def get_candidate_ids(self) -> List[str]:
          return ["yes", "no"]

  pancake = FlaskPancake(
      group_funcs={"user": get_group_user, "superuser": get_group_superuser}
      # alternatively if using the class-based approach:
      # group_funcs={"user": get_group_user, "superuser": IsSuperuser}
  )
  # Or, if importing a function from somewhere isn't possible, a string based
  # approach can be used.
  # Separate the the fully qualified module path from the function with a `:`
  pancake = FlaskPancake(
      group_funcs={
          "user", "my.app.account.utils:get_group_user",
          "superuser", "my.app.account.utils:get_group_superuser",
          # alternatively if using the class-based approach:
          "superuser", "my.app.account.utils:IsSuperuser",
      }
  )
  ```

  In the example, whenever one checks for a `Flag`, FlaskPancake would check if
  a value has been set in the following order:

  1. Is the flag disable/enable for the current user?
  1. If not, is the flag disable/enabled for superusers/non-superusers?
  1. If not, is the flag disable/enabled by default?

* `Sample`s, have a global "ratio" of 0 - 100%. On the first check of a sample
  in a request, a random value is checked within these bounds. If it's lower or
  equal the set value, it's active, if it's larger, it's inactive.

  Due to the randomness, samples store their state in a request context (Flask's
  `g` context object). Additionally, in order to provide consistent behavior for
  a user between requests, the values of the used samples in a request are
  stored in a cookie in the user's browser. They are then loaded on the next
  request again and thus provide a stable behavior across requests.

  That means, despite the randomness involved, this behavior is actually safe:

  ```python
  def foo():
      if MY_SAMPLE.is_active():
          # do something
          pass
      ...
      if MY_SAMPLE.is_active():
          # do more
          pass
  ```

The persisted state for all three types of feature flags can be cleared, using
the `clear()` method.

Similarly, one can change the persisted state for `Flag`s and `Switch`es using
their `disable()` and `enable()` methods. `Sample`s can be updated using their
`set(value: float)` method.

When using `Flag`s, there are `clear_group(group_id)` and
`clear_all_group(group_id)` methods, to clear the state for the current or all
users within a group. Along the same line, there are `disable_group(group_id)`
and `enable_group(group_id)` to set the group's state the current user is part
of.

### Web API

`flask-pancake` provides an API endpoint that shows all available `Flag`s,
`Sample`s and `Switch`es and their corresponding states under the `/overview`
route within the blueprint. It also provides a JSON API to get the status for
all feature flags for the current user under the `/status` route. The APIs can
be enabled by registering a Flask blueprint:

```python
from flask import Flask
from flask_pancake import FlaskPancake, blueprint

app = Flask(__name__)
app.secret_key = "s3cr!t"
pancake = FlaskPancake(app)
app.register_blueprint(blueprint, url_prefix="/pancakes")
```

**WARNING:** The API is not secured in any way! You should use Flask's
[`Blueprint.before_request()`](https://flask.palletsprojects.com/en/1.1.x/api/?highlight=register_blueprint#flask.Blueprint.before_request)
feature to add some authentication for the `/overview` endpoint. Check the
[`complex_app.py`](https://github.com/MarkusH/flask-pancake/blob/master/examples/complex_app.py)
for an example.

**NOTE:** The `/status` API endpoint is meant to be used by front-end
applications to load the status of all `Flag`s,
`Sample`s and `Switch`es and have them readily available in the front-end. If
one does not want to expose some feature flags to the front-end via the
`/status` endpoint, separate the feature flags into two `FlaskPancake` extension
instances and only allow access to the `/status` endpoint serving the front-end
feature flags.

As noted above, `Sample`s store their state in cookies between requests. The
cookie name defaults to the name of the extension, but can be set explicitly
using the `cookie_name` argument when instantiating the `FlaskPancake()`
extension. The same goes for the cookie options: by default, cookies will be set
with the `HttpOnly` and `SameSite=Lax` attributes. The cookie options are passed
through to [Werkzeug's `set_cookie()` method](https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/?highlight=set_cookie#werkzeug.wrappers.BaseResponse.set_cookie):

```python
from flask import Flask
from flask_pancake import FlaskPancake

app = Flask(__name__)
app.secret_key = "s3cr!t"
pancake = FlaskPancake(
    app,
    name="feature-flags",
    cookie_name="ff",
    cookie_options={"httponly": True, "samesite": "Lax", "secure": True},
)
```

### Command Line Interface

`flask-pancake` comes with a CLI that hooks into Flask's own CLI. The same way you can call `flask run` to start your application in development mode you can call `flask pancake`. Here are some examples:

```console
$ flask pancake
Usage: flask pancake [OPTIONS] COMMAND [ARGS]...

  Commands to manage flask-pancake flags, samples, and switches.

Options:
  --help  Show this message and exit.

Commands:
  flags
  samples
  switches

$ flask pancake flags list
DO_SOMETHING_ELSE: Yes (default: Yes)
FOO_CAN_DO: No (default: No)

$ flask pancake flags enable FOO_CAN_DO
Flag 'FOO_CAN_DO' enabled.

$ flask pancake flags list
DO_SOMETHING_ELSE: Yes (default: Yes)
FOO_CAN_DO: Yes (default: No)
```
