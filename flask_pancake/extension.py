from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, Optional, Union

from cached_property import cached_property

from .constants import EXTENSION_NAME
from .registry import registry
from .utils import import_from_string

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
        get_user_id_func: Optional[Union[str, Callable[[], str]]] = None,
    ) -> None:
        self.redis_extension_name = redis_extension_name
        self._get_user_id_func = get_user_id_func
        self.name = name

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.extensions[self.name] = self

    @cached_property
    def get_user_id_func(self) -> Optional[Callable[[], str]]:
        if isinstance(self._get_user_id_func, str):
            return import_from_string(self._get_user_id_func)
        return self._get_user_id_func

    @property
    def flags(self) -> Dict[str, Flag]:
        return registry.flags(self.name)

    @property
    def switches(self) -> Dict[str, Switch]:
        return registry.switches(self.name)

    @property
    def samples(self) -> Dict[str, Sample]:
        return registry.samples(self.name)
