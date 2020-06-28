=========
CHANGELOG
=========

Unreleased
==========

0.4.0 - 2020-06-28
==================

- Added Flask CLI commands to manage flags, samples, and switches. Check out
  ``flask pancake --help``:

  .. code-block:: console

     $ flask pancake --help
     Usage: flask pancake [OPTIONS] COMMAND [ARGS]...

       Commands to manage flask-pancake flags, samples, and switches.

     Options:
       --help  Show this message and exit.

     Commands:
       flags
       samples
       switches

0.3.0 - 2020-04-26
==================

- BREAKING: Added ability for multiple different groups in ``Flag``\s. This
  provides the ability to e.g. enable a flag for all admins and developers, for
  while disabling if for everyone else.

0.2.0 - 2020-01-26
==================

- Added support for multiple ``FlaskPancake`` instances in a single app. To use
  this, pass an additional ``name`` argument when creating a ``FlaskPancake``
  instance.

- The format for Redis keys for user flags was changed from
  ``FLAG:user:<uid>:<FLAG_NAME_UPPER>`` to ``FLAG:<FLAG_NAME_UPPER>:user:<uid>``.

0.1.0 - 2020-01-22
==================

- Initial release. There are "Flags", "Samples", and "Switches" to control your
  application.
