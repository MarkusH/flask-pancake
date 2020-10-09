from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

from cached_property import cached_property

from .constants import EXTENSION_NAME
from .registry import registry
from .utils import GroupFuncType, import_from_string, load_cookies, store_cookies

if TYPE_CHECKING:
    from flask import Flask

    from .flags import Flag, Sample, Switch

__all__ = ["FlaskPancake"]


class FlaskPancake:
    def __init__(
        self,
        app: Flask = None,
        *,
        name: str = EXTENSION_NAME,
        redis_extension_name: str = "redis",
        group_funcs: Optional[
            Dict[str, Union[str, Type[GroupFunc], GroupFunc, GroupFuncType]]
        ] = None,
        cookie_name=None,
        cookie_options: Dict[str, Any] = None,
    ) -> None:
        self.redis_extension_name = redis_extension_name
        self._group_funcs = group_funcs
        self.name = name
        self.cookie_name = cookie_name or self.name
        self.cookie_options = cookie_options or {"httponly": True, "samesite": "Lax"}

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.extensions[self.name] = self
        app.before_request(load_cookies(self))
        app.after_request(store_cookies(self))

    @cached_property
    def group_funcs(self) -> Optional[Dict[str, GroupFunc]]:
        if self._group_funcs is None:
            return None
        ret = {}
        for key, value in self._group_funcs.items():
            if isinstance(value, str):
                value = import_from_string(value)
            if isinstance(value, type) and issubclass(value, GroupFunc):
                value = value()
            if isinstance(value, GroupFunc):
                ret[key] = value
            elif callable(value):
                ret[key] = FunctionGroupFunc(value)
            else:
                raise ValueError(f"Invalid group function {value!r} for {key!r}.")

        return ret

    @property
    def flags(self) -> Dict[str, Flag]:
        return registry.flags(self.name)

    @property
    def switches(self) -> Dict[str, Switch]:
        return registry.switches(self.name)

    @property
    def samples(self) -> Dict[str, Sample]:
        return registry.samples(self.name)


class GroupFunc(abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> Optional[str]:
        ...  # pragma: no cover

    @abc.abstractmethod
    def get_candidate_ids(self) -> List[str]:
        ...  # pragma: no cover


class FunctionGroupFunc(GroupFunc):
    def __init__(self, func: Callable[[], Optional[str]]):
        self._func = func

    def __call__(self) -> Optional[str]:
        return self._func()

    def get_candidate_ids(self) -> List[str]:
        sub_func = getattr(self._func, "get_candidate_ids", None)
        if sub_func:
            return sub_func()
        return []

    def __eq__(self, other) -> bool:
        return isinstance(other, FunctionGroupFunc) and self._func == other._func
