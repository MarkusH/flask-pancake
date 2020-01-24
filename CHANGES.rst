=========
CHANGELOG
=========

Unreleased
==========

- Added support for multiple ``FlaskPancake`` instances in a single app.

- The format for Redis keys for user flags was changed from
  ``FLAG:user:<uid>:<FLAG_NAME_UPPER>`` to ``FLAG:<FLAG_NAME_UPPER>:user:<uid>``.

0.1.0 - 2020-01-22
==================

- Initial release. There are "Flags", "Samples", and "Switches" to control your
  application.
