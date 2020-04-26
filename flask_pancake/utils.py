import importlib
from typing import Callable

GroupFunc = Callable[[], str]


def import_from_string(fqn: str) -> GroupFunc:
    if fqn.count(":") != 1:
        raise ValueError(
            f"Invalid function reference '{fqn}'. The format is "
            "`path.to.module:function`."
        )
    module_name, attr = fqn.split(":")
    module = importlib.import_module(module_name)
    return getattr(module, attr)
