=========
CHANGELOG
=========

Unreleased
==========

0.5.1 - 2020-10-13
==================

- Fixed a packaging bug that prevented the HTML template for the overview page
  to be included.

0.5.0 - 2020-10-13
==================

- BREAKING: Added persistence of the status of `Sample`s between requests. With
  this change, checking for a sample within the same request multiple times
  will yield the same status each time. And to ensure the same status across
  requests, the status is stored in a cookie.

- Added a JSON API endpoint under ``GET /status`` that exposes which flags,
  samples, or switches are active for the current user.

- Added an HTML and JSON API endpoint under ``GET /overview`` that shows the
  status of each flag, sample, or switch, including the status of a flag for
  each group's object.

- Added support for class-based group functions, which can also expose a set of
  "candidate IDs". These candidate IDs are used in the new API overview.

- Updated the CLI commands to show the default value when listing flags,
  samples, or switches.

- Added the ``flask pancake flags list-group`` CLI command.

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
