import importlib
from typing import Any


def import_from_string(fqn: str) -> Any:
    module_name, _, attr = fqn.partition(":")
    module = importlib.import_module(module_name)
    if attr:
        return getattr(module, attr)
    return module
