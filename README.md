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
  make use of Flags, one needs to define at least one function that returns a
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

  pancake = FlaskPancake(
      group_funcs={"user", get_group_user, "superuser", get_group_superuser}
  )
  # Or, if importing a function from somewhere isn't possible, a string based
  # approach can be used.
  # Separate the the fully qualified module path from the function with a `:`
  pancake = FlaskPancake(
      group_funcs={
          "user", "my.app.account.utils:get_group_user",
          "superuser", "my.app.account.utils:get_group_superuser",
      }
  )
  ```

  In the example, whenever one checks for a `Flag`, FlaskPancake would check if
  a value has been set in the following order:

  1. Is the flag disable/enable for the current user?
  1. If not, is the flag disable/enabled for superusers/non-superusers?
  1. If not, is the flag disable/enabled by default?

* `Sample`s, have a global "ratio" of 0 - 100%. Each time a check is done on a
  sample, a random value is checked within these bounds. Hence:

  ```python
  # DO THIS!
  def foo():
      is_active = MY_SAMPLE.is_active()
      if is_active:
          # do something
          pass
      ...
      if is_active:
          # do more
          pass

  # DO NOT DO THIS!
  def foo():
      if MY_SAMPLE.is_active():
          # do something
          pass
      ...
      if MY_SAMPLE.is_active():
          # do more
          pass
  ```

  In the second example, each call to `is_active()` will be evaluated again.
  Thus, the first block might be executed, but the second might not (or vice
  versa).

The persisted state for all three types of feature flags can be cleared, using
the `clear()` method.

Similarly, one can change the persisted state for Flags and Switches using
their `disable()` and `enable()` methods. Samples can be updated using their
`set(value: float)` method.

When using `Flag`s, there are `clear_group(group_id)` and
`clear_all_group(group_id)` methods, to clear the state for the current or all
users within a group. Along the same line, there are `disable_group(group_id)`
and `enable_group(group_id)` to set the group's state the current user is part
of.
