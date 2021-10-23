from flask import Blueprint, abort, current_app, render_template, request
from flask.json import jsonify
from jinja2 import TemplateNotFound

from .constants import EXTENSION_NAME
from .extension import FlaskPancake

bp = Blueprint("pancake", __name__, template_folder="templates")


def aggregate_data(ext: FlaskPancake):
    if ext.group_funcs:
        group_ids = list(ext.group_funcs.keys())
        flags = [
            {
                "name": flag.name,
                "default": flag.default,
                "is_active": flag.is_active_globally(),
                "groups": {
                    group_id: {
                        object_id: flag.is_active_group(
                            group_id=group_id, object_id=object_id
                        )
                        for object_id in func.get_candidate_ids()
                    }
                    for group_id, func in ext.group_funcs.items()
                },
            }
            for flag in ext.flags.values()
        ]
    else:
        group_ids = []
        flags = [
            {
                "name": flag.name,
                "default": flag.default,
                "is_active": flag.is_active_globally(),
                "groups": {},
            }
            for flag in ext.flags.values()
        ]

    samples = [
        {"name": sample.name, "default": sample.default, "value": sample.get()}
        for sample in ext.samples.values()
    ]
    switches = [
        {
            "name": switch.name,
            "default": switch.default,
            "is_active": switch.is_active(),
        }
        for switch in ext.switches.values()
    ]

    return {
        "name": ext.name,
        "group_ids": group_ids,
        "flags": flags,
        "samples": samples,
        "switches": switches,
    }


def aggregate_is_active_data(ext: FlaskPancake):
    flags = [
        {"name": flag.name, "is_active": flag.is_active()}
        for flag in ext.flags.values()
    ]

    samples = [
        {"name": sample.name, "is_active": sample.is_active()}
        for sample in ext.samples.values()
    ]
    switches = [
        {"name": switch.name, "is_active": switch.is_active()}
        for switch in ext.switches.values()
    ]

    return {
        "flags": flags,
        "samples": samples,
        "switches": switches,
    }


@bp.route("/overview", defaults={"pancake": EXTENSION_NAME})
@bp.route("/overview/<pancake>")
def overview(pancake):
    ext = current_app.extensions.get(pancake)
    if ext is None or not isinstance(ext, FlaskPancake):
        return "Unknown", 404

    context = aggregate_data(ext)

    if request.accept_mimetypes.accept_html:
        try:
            return render_template("flask_pancake/overview.html", **context)
        except TemplateNotFound:  # pragma: no cover
            abort(404)
    else:
        return jsonify(context)


@bp.route("/status", defaults={"pancake": EXTENSION_NAME})
@bp.route("/status/<pancake>")
def status(pancake):
    ext = current_app.extensions.get(pancake)
    if ext is None or not isinstance(ext, FlaskPancake):
        return "Unknown", 404
    context = aggregate_is_active_data(ext)
    return jsonify(context)
