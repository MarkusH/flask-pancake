from __future__ import annotations

import abc
import random
from typing import TYPE_CHECKING, Generic, Optional, TypeVar

from cached_property import cached_property
from flask import current_app

from .constants import EXTENSION_NAME, RAW_FALSE, RAW_TRUE
from .registry import registry

if TYPE_CHECKING:
    from flask_redis import FlaskRedis

    from .extension import FlaskPancake


__all__ = ["Flag", "Sample", "Switch"]


DEFAULT_TYPE = TypeVar("DEFAULT_TYPE")


class AbstractFlag(abc.ABC, Generic[DEFAULT_TYPE]):
    name: str
    default: DEFAULT_TYPE
    extension: str

    def __init__(
        self, name: str, default: DEFAULT_TYPE, extension: Optional[str] = None
    ) -> None:
        self.name = name
        self.set_default(default)
        self.extension = extension if extension is not None else EXTENSION_NAME

        registry.register(self)

    def set_default(self, default: DEFAULT_TYPE) -> None:
        self.default = default

    @cached_property
    def ext(self) -> "FlaskPancake":
        return current_app.extensions[self.extension]

    @cached_property
    def _redis_client(self) -> FlaskRedis:
        return current_app.extensions[self.ext.redis_extension_name]

    @cached_property
    def key(self) -> str:
        extension = ""
        if self.extension != EXTENSION_NAME:
            extension = f":{self.extension}"
        return f"{self.__class__.__name__.upper()}:{self.name.upper()}{extension}"

    @abc.abstractmethod
    def is_active(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    def clear(self) -> None:
        self._redis_client.delete(self.key)


class BaseFlag(AbstractFlag[bool], abc.ABC):
    def set_default(self, default: bool) -> None:
        if int(default) not in {0, 1}:
            raise ValueError(
                f"Default value for {self.__class__.__name__.lower()} {self.name} "
                f"must be True or False."
            )
        super().set_default(default)

    def is_active(self) -> bool:
        self._redis_client.setnx(self.key, int(self.default))
        return self._redis_client.get(self.key) == RAW_TRUE

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
        return f"{self.key}:user:{uid}"

    def is_active(self) -> bool:
        user_key = self.user_key
        if user_key is not None:
            value = self._redis_client.get(user_key)
            if value == RAW_TRUE:
                return True
            elif value == RAW_FALSE:
                return False

        return super().is_active()

    @cached_property
    def _track_key_users(self):
        return f"{self.__class__.__name__.upper()}:track:users"

    def _track_user(self, key):
        self._redis_client.sadd(self._track_key_users, key)

    def clear_user(self) -> None:
        uk = self.user_key
        self._redis_client.delete(uk)
        self._redis_client.srem(self._track_key_users, uk)

    def clear_all_users(self) -> None:
        keys = self._redis_client.smembers(self._track_key_users)
        if keys:
            self._redis_client.srem(self._track_key_users, *keys)
            self._redis_client.delete(*keys)

    def disable_user(self) -> None:
        uk = self.user_key
        self._track_user(uk)
        self._redis_client.set(uk, 0)

    def enable_user(self) -> None:
        uk = self.user_key
        self._track_user(uk)
        self._redis_client.set(uk, 1)


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
        if not (0 <= value <= 100):
            raise ValueError(
                f"Value for sample {self.name} must be in the range [0, 100]."
            )
        self._redis_client.set(self.key, value)
