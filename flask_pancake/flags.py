from __future__ import annotations

import abc
import random
from typing import TYPE_CHECKING, Dict, Generic, Optional, Tuple, TypeVar

from cached_property import cached_property
from flask import current_app

from .constants import EXTENSION_NAME, RAW_FALSE, RAW_TRUE
from .registry import registry

if TYPE_CHECKING:
    from flask_redis import FlaskRedis

    from .extension import FlaskPancake
    from .utils import GroupFunc


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

    @property
    def ext(self) -> "FlaskPancake":
        return current_app.extensions[self.extension]

    @property
    def _redis_client(self) -> FlaskRedis:
        return current_app.extensions[self.ext.redis_extension_name]

    @cached_property
    def key(self) -> str:
        return f"{self.__class__.__name__.upper()}:{self.extension}:{self.name.upper()}"

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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keys: Dict[str, Tuple[str, str]] = {}

    def _get_group_keys(self, group_id: str) -> Tuple[str, str]:
        if group_id in self._keys:
            return self._keys[group_id]
        if self.ext.group_funcs is None:
            raise RuntimeError(
                f"No group_funcs defined on FlaskPancake extension '{self.extension}'. "
                "If you don't have users or other types of groups in your application "
                "and want a global flag to turn things on and off, use a `Switch` "
                "instead."
            )
        if group_id not in self.ext.group_funcs:
            raise RuntimeError(
                f"Invalid group identifer '{group_id}'. This group doesn't seem to be "
                f"registered in the FlaskPancake extension '{self.extension}'."
            )

        object_key = f"FLAG:{self.extension}:k:{group_id}:{self.name.upper()}"
        tracking_key = f"FLAG:{self.extension}:t:{group_id}:{self.name.upper()}"
        r = self._keys[group_id] = (object_key, tracking_key)
        return r

    def _get_object_key(
        self, group_id: str, *, func: GroupFunc = None, object_id: str = None
    ):
        object_key_prefix, _ = self._get_group_keys(group_id)
        if object_id is None:
            if func is None:
                func = self.ext.group_funcs[group_id]
            object_id = func()
        if object_id is None:
            return None
        return f"{object_key_prefix}:{object_id}"

    def is_active(self) -> bool:
        if self.ext.group_funcs:
            for group_id, func in self.ext.group_funcs.items():
                object_key = self._get_object_key(group_id, func=func)
                if object_key is not None:
                    value = self._redis_client.get(object_key)
                    if value == RAW_TRUE:
                        return True
                    elif value == RAW_FALSE:
                        return False

        return super().is_active()

    def _track_object(self, group_id: str, object_key: str):
        self._redis_client.sadd(self._get_group_keys(group_id)[1], object_key)

    def clear_group(self, group_id: str, *, object_id: str = None):
        object_key = self._get_object_key(group_id, object_id=object_id)
        if object_key is None:
            raise RuntimeError(f"Cannot derive identifier for group '{group_id}'")
        self._redis_client.delete(object_key)
        self._redis_client.srem(self._get_group_keys(group_id)[1], object_key)

    def clear_all_group(self, group_id: str) -> None:
        _, tracking_key = self._get_group_keys(group_id)
        object_keys = self._redis_client.smembers(tracking_key)
        if object_keys:
            self._redis_client.delete(*object_keys)
            self._redis_client.srem(tracking_key, *object_keys)

    def disable_group(self, group_id: str, *, object_id: str = None) -> None:
        object_key = self._get_object_key(group_id, object_id=object_id)
        if object_key is None:
            raise RuntimeError(f"Cannot derive identifier for group '{group_id}'")
        self._track_object(group_id, object_key)
        self._redis_client.set(object_key, 0)

    def enable_group(self, group_id: str, *, object_id: str = None) -> None:
        object_key = self._get_object_key(group_id, object_id=object_id)
        if object_key is None:
            raise RuntimeError(f"Cannot derive identifier for group '{group_id}'")
        self._track_object(group_id, object_key)
        self._redis_client.set(object_key, 1)


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

    # def clear(self) -> None:
    #     self._redis_client.delete(self.key)

    def set(self, value: float) -> None:
        if not (0 <= value <= 100):
            raise ValueError(
                f"Value for sample {self.name} must be in the range [0, 100]."
            )
        self._redis_client.set(self.key, value)
