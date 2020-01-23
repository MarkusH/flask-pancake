from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .flags import Flag, Sample, Switch


__all__ = ["registry"]


class Registry:
    def __init__(self) -> None:
        self._flags: Dict[str, Dict[str, Flag]] = {}
        self._samples: Dict[str, Dict[str, Sample]] = {}
        self._switches: Dict[str, Dict[str, Switch]] = {}

    def register_flag(self, flag: Flag) -> None:
        self._flags[flag.extension] = {flag.name: flag}

    def register_sample(self, sample: Sample) -> None:
        self._samples[sample.extension] = {sample.name: sample}

    def register_switch(self, switch: Switch) -> None:
        self._switches[switch.extension] = {switch.name: switch}

    def flags(self, extension: str):
        return self._flags.get(extension, {})

    def samples(self, extension: str):
        return self._samples.get(extension, {})

    def switches(self, extension: str):
        return self._switches.get(extension, {})


registry = Registry()
