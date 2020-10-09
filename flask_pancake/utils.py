import importlib
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import click
from flask import Response, current_app, g, request
from itsdangerous import BadData, URLSafeSerializer

from .constants import COOKIE_SALT

if TYPE_CHECKING:
    from .extension import FlaskPancake

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


def decode_sample_state(s: Union[str, bytes]) -> Any:
    if current_app.secret_key is None:
        raise RuntimeError(
            "Cannot load sample flags cookie since app.SECRET_KEY is not set."
        )
    serializer = URLSafeSerializer(current_app.secret_key, COOKIE_SALT)
    return serializer.loads(s)


def encode_sample_state(o: Any) -> str:
    if current_app.secret_key is None:
        raise RuntimeError(
            "Cannot store sample flags cookie since app.SECRET_KEY is not set."
        )
    serializer = URLSafeSerializer(current_app.secret_key, COOKIE_SALT)
    return serializer.dumps(o)


def load_cookies(ext: "FlaskPancake") -> Callable[[], Optional[Any]]:
    def _wrapper():
        data = request.cookies.get(ext.cookie_name)
        if data is not None:
            try:
                g.setdefault("pancakes", {})[ext.name] = decode_sample_state(data)
            except BadData:
                pass

    return _wrapper


def store_cookies(ext: "FlaskPancake") -> Callable[[Response], Response]:
    def _wrapper(response: Response) -> Response:
        data = g.get("pancakes", {}).get(ext.name)
        if data:
            response.set_cookie(
                ext.cookie_name, value=encode_sample_state(data), **ext.cookie_options
            )
        return response

    return _wrapper
