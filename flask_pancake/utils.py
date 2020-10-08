import importlib
from typing import Callable, Optional

import click

GroupFuncType = Callable[[], Optional[str]]


def import_from_string(fqn: str) -> GroupFuncType:
    if fqn.count(":") != 1:
        raise ValueError(
            f"Invalid function reference '{fqn}'. The format is "
            "`path.to.module:function`."
        )
    module_name, attr = fqn.split(":")
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def format_flag_state_cli(value: Optional[bool]) -> str:
    if value is None:
        return click.style("N/A", fg="yellow")
    if value:
        return click.style("Yes", fg="green")
    return click.style("No", fg="red")
