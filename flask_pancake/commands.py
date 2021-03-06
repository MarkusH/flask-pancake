import click
from flask import current_app
from flask.cli import AppGroup

from .extension import EXTENSION_NAME
from .utils import format_flag_state_cli

pancake_cli = AppGroup(
    "pancake", help="Commands to manage flask-pancake flags, samples, and switches."
)


# FLAGS


flags_cli = AppGroup("flags")
pancake_cli.add_command(flags_cli)


@flags_cli.command("clear")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def flag_clear(extension, name):
    current_app.extensions[extension].flags[name].clear()
    click.echo(f"Flag '{name}' " + click.style("cleared", fg="yellow") + ".")


@flags_cli.command("clear-group")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
@click.argument("group")
@click.argument("id")
def flag_clear_group(extension, name, group, id):
    current_app.extensions[extension].flags[name].clear_group(
        group_id=group, object_id=id
    )
    click.echo(
        f"Object {id!r} in group '{group}' for flag '{name}' "
        + click.style("cleared", fg="yellow")
        + "."
    )


@flags_cli.command("disable")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def flag_disable(extension, name):
    current_app.extensions[extension].flags[name].disable()
    click.echo(f"Flag '{name}' " + click.style("disabled", fg="red") + ".")


@flags_cli.command("disable-group")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
@click.argument("group")
@click.argument("id")
def flag_disable_group(extension, name, group, id):
    current_app.extensions[extension].flags[name].disable_group(
        group_id=group, object_id=id
    )
    click.echo(
        f"Object {id!r} in group '{group}' for flag '{name}' "
        + click.style("disabled", fg="red")
        + "."
    )


@flags_cli.command("enable")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def flag_enable(extension, name):
    current_app.extensions[extension].flags[name].enable()
    click.echo(f"Flag '{name}' " + click.style("enabled", fg="green") + ".")


@flags_cli.command("enable-group")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
@click.argument("group")
@click.argument("id")
def flag_enable_group(extension, name, group, id):
    current_app.extensions[extension].flags[name].enable_group(
        group_id=group, object_id=id
    )
    click.echo(
        f"Object {id!r} in group '{group}' for flag '{name}' "
        + click.style("enabled", fg="green")
        + "."
    )


@flags_cli.command("list")
@click.option("--extension", default=EXTENSION_NAME)
def flag_list(extension):
    for name, instance in sorted(current_app.extensions[extension].flags.items()):
        default = format_flag_state_cli(instance.default)
        globally = format_flag_state_cli(instance.is_active_globally())
        click.echo(f"{name}: {globally} (default: {default})")


@flags_cli.command("list-group")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("group")
@click.argument("id")
def flag_list_group(extension, group, id):
    for name, instance in sorted(current_app.extensions[extension].flags.items()):
        default = format_flag_state_cli(instance.default)
        value = instance.is_active_group(group_id=group, object_id=id)
        for_group = format_flag_state_cli(value)
        click.echo(f"{name}: {for_group} (default: {default})")


# SAMPLES


samples_cli = AppGroup("samples")
pancake_cli.add_command(samples_cli)


@samples_cli.command("clear")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def sample_clear(extension, name):
    current_app.extensions[extension].samples[name].clear()
    click.echo(f"Sample '{name}' " + click.style("cleared", fg="yellow") + ".")


@samples_cli.command("list")
@click.option("--extension", default=EXTENSION_NAME)
def sample_list(extension):
    for name, instance in sorted(current_app.extensions[extension].samples.items()):
        default = click.style(str(instance.default), fg="blue")
        value = click.style(str(instance.get()), fg="blue")
        click.echo(f"{name}: {value} (default: {default})")


def validate_set(ctx, param, value):
    if not (0 <= value <= 100):
        raise click.BadParameter("Value for sample must be in the range [0, 100].")
    return value


@samples_cli.command("set")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
@click.argument("value", type=float, callback=validate_set)
def sample_set(extension, name, value):
    current_app.extensions[extension].samples[name].set(value)
    click.echo(f"Sample '{name}' set to '" + click.style(str(value), fg="blue") + "'.")


# SWITCHES


switches_cli = AppGroup("switches")
pancake_cli.add_command(switches_cli)


@switches_cli.command("clear")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def switch_clear(extension, name):
    current_app.extensions[extension].switches[name].clear()
    click.echo(f"Switch '{name}' " + click.style("cleared", fg="yellow") + ".")


@switches_cli.command("disable")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def switch_disable(extension, name):
    current_app.extensions[extension].switches[name].disable()
    click.echo(f"Switch '{name}' " + click.style("disabled", fg="red") + ".")


@switches_cli.command("enable")
@click.option("--extension", default=EXTENSION_NAME)
@click.argument("name")
def switch_enable(extension, name):
    current_app.extensions[extension].switches[name].enable()
    click.echo(f"Switch '{name}' " + click.style("enabled", fg="green") + ".")


@switches_cli.command("list")
@click.option("--extension", default=EXTENSION_NAME)
def switch_list(extension):
    for name, instance in sorted(current_app.extensions[extension].switches.items()):
        default = format_flag_state_cli(instance.default)
        value = format_flag_state_cli(instance.is_active())
        click.echo(f"{name}: {value} (default: {default})")
