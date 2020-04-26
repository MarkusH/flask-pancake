from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from cached_property import cached_property

from .constants import EXTENSION_NAME
from .registry import registry
from .utils import GroupFunc, import_from_string

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
        group_funcs: Optional[Dict[str, Union[str, GroupFunc]]] = None,
    ) -> None:
        self.redis_extension_name = redis_extension_name
        self._group_funcs = group_funcs
        self.name = name

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.extensions[self.name] = self

    @cached_property
    def group_funcs(self) -> Optional[Dict[str, GroupFunc]]:
        if self._group_funcs is None:
            return None
        return {
            key: (import_from_string(value) if isinstance(value, str) else value)
            for key, value in self._group_funcs.items()
        }

    @property
    def flags(self) -> Dict[str, Flag]:
        return registry.flags(self.name)

    @property
    def switches(self) -> Dict[str, Switch]:
        return registry.switches(self.name)

    @property
    def samples(self) -> Dict[str, Sample]:
        return registry.samples(self.name)
