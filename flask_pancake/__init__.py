from __future__ import annotations

import abc
import random
import importlib
from typing import TYPE_CHECKING, Callable, Dict, Generic, TypeVar, Any, Union, Optional

from cached_property import cached_property
from flask import current_app

if TYPE_CHECKING:
    from flask import Flask
    from flask_redis import FlaskRedis


DEFAULT_TYPE = TypeVar("DEFAULT_TYPE")
EXTENSION_NAME = "pancake"


_FLAGS: Dict[str, Flag] = {}
_SWITCHES: Dict[str, Switch] = {}
_SAMPLES: Dict[str, Sample] = {}


def import_from_string(fqn: str) -> Any:
    module_name, _, attr = fqn.partition(":")
    module = importlib.import_module(module_name)
    if attr:
        return getattr(module, attr)
    return module


class FlaskPancake:
    def __init__(
        self,
        app: Flask = None,
        *,
        redis_extension_name: str = "redis",
        get_user_id_func: Optional[Union[str, Callable[[], str]]] = None,
    ) -> None:
        self.redis_extension_name = redis_extension_name
        self._get_user_id_func = get_user_id_func

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.extensions[EXTENSION_NAME] = self

    @cached_property
    def get_user_id_func(self) -> Optional[Callable[[], str]]:
        if isinstance(self._get_user_id_func, str):
            return import_from_string(self._get_user_id_func)
        return self._get_user_id_func

    @property
    def flags(self) -> Dict[str, Flag]:
        return _FLAGS

    @property
    def switches(self) -> Dict[str, Switch]:
        return _SWITCHES

    @property
    def samples(self) -> Dict[str, Sample]:
        return _SAMPLES


class AbstractFlag(abc.ABC, Generic[DEFAULT_TYPE]):
    name: str

    def __init__(self, name: str, default: DEFAULT_TYPE) -> None:
        self.name = name
        self.set_default(default)

        if isinstance(self, Flag):
            _FLAGS[name.upper()] = self
        elif isinstance(self, Switch):
            _SWITCHES[name.upper()] = self
        elif isinstance(self, Sample):
            _SAMPLES[name.upper()] = self

    def set_default(self, default: DEFAULT_TYPE) -> None:
        self.default = default

    @cached_property
    def ext(self) -> FlaskPancake:
        return current_app.extensions[EXTENSION_NAME]

    @cached_property
    def _redis_client(self) -> FlaskRedis:
        return current_app.extensions[self.ext.redis_extension_name]

    @cached_property
    def key(self) -> str:
        return f"{self.__class__.__name__.upper()}:{self.name.upper()}"

    @abc.abstractmethod
    def is_active(self) -> bool:
        ...

    def clear(self) -> None:
        self._redis_client.delete(self.key)


class BaseFlag(AbstractFlag[bool], abc.ABC):
    def set_default(self, default: bool) -> None:
        if int(default) not in {0, 1}:
            raise ValueError(
                f"Default value for switch {self.name} must be True or False."
            )
        super().set_default(default)

    def is_active(self) -> bool:
        self._redis_client.setnx(self.key, int(self.default))
        return self._redis_client.get(self.key) == b"1"

    def disable(self) -> None:
        self._redis_client.set(self.key, 0)

    def enable(self) -> None:
        self._redis_client.set(self.key, 1)


class Flag(BaseFlag):
    """
    A feature flag.

    Flags are active (or not) on a per-request / user basis.
    """

    @property
    def user_key(self) -> Optional[str]:
        get_user_id_func = self.ext.get_user_id_func
        if get_user_id_func is None:
            raise RuntimeError(
                "No get_user_id_func defined on FlaskPancake. If you don't "
                "have users in your application and want a global flag to "
                "turn things on and off, use a `Switch` instead."
            )
        uid = get_user_id_func()
        if uid is None:
            return None
        return f"{self.__class__.__name__.upper()}:user:{uid}:{self.name.upper()}"

    def is_active(self) -> bool:
        user_key = self.user_key
        if user_key is not None:
            value = self._redis_client.get(user_key)
            if value == b"1":
                return True

        return super().is_active()

    def clear_user(self) -> None:
        self._redis_client.delete(self.user_key)

    def disable_user(self) -> None:
        self._redis_client.set(self.user_key, 0)

    def enable_user(self) -> None:
        self._redis_client.set(self.user_key, 1)


class Switch(BaseFlag):
    """
    A feature switch.

    Switches are active or inactive, globally.
    """


class Sample(AbstractFlag[float]):
    """
    A sample of users.

    A sample is active some percentage of the time, but is not connected to users
    or requests.
    """

    def set_default(self, default: float) -> None:
        if not (0 <= default <= 100):
            raise ValueError(
                f"Default value for sample {self.name} must be in the range [0, 100]."
            )
        super().set_default(default)

    def is_active(self) -> bool:
        self._redis_client.setnx(self.key, self.default)
        value = self._redis_client.get(self.key)
        return random.uniform(0, 100) <= float(value)

    def set(self, value: float) -> None:
        self._redis_client.set(self.key, value)
