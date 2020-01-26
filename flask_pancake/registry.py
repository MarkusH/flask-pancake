from __future__ import annotations

from typing import Dict

__all__ = ["registry"]


class Registry:
    def __init__(self) -> None:
        self._flags: Dict[str, Dict[str, Flag]] = {}
        self._samples: Dict[str, Dict[str, Sample]] = {}
        self._switches: Dict[str, Dict[str, Switch]] = {}

    def register(self, flag: AbstractFlag) -> None:
        if isinstance(flag, Flag):
            self._flags.setdefault(flag.extension, {})[flag.name] = flag
        elif isinstance(flag, Sample):
            self._samples.setdefault(flag.extension, {})[flag.name] = flag
        elif isinstance(flag, Switch):
            self._switches.setdefault(flag.extension, {})[flag.name] = flag
        else:
            raise TypeError(f"Cannot register class of type {flag.__class__.__name__}")

    def flags(self, extension: str):
        return self._flags.get(extension, {})

    def samples(self, extension: str):
        return self._samples.get(extension, {})

    def switches(self, extension: str):
        return self._switches.get(extension, {})

    def __clear__(self):
        self._flags.clear()
        self._samples.clear()
        self._switches.clear()


registry = Registry()

from .flags import AbstractFlag, Flag, Sample, Switch  # isort:skip # noqa
