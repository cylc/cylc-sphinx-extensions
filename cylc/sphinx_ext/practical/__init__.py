# -----------------------------------------------------------------------------
# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) NIWA & British Crown (Met Office) & Contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------
"""Directives for use in practical exercises.

.. _example-tutorial:

Directives
----------

.. rst:directive:: practical

   Directive for practical exercise.

   .. rst-example::

      .. practical::

         Some instructions here.

         .. practical::

            Here is an exercise to complete

.. rst:directive:: practical-extension

   Directive for practical exercise extensions.

   .. rst-example::

      .. practical-extension::

         Here is a follow-on exercise

.. rst:directive:: spoiler

   Directive for content which is hidden by default.

   .. rst-example::

      .. spoiler:: Spoiled warning

         Hidden text which will display with class ``warning``.

   Arguments
      title
         Title to give the admonition
      class
         The admonition class to give this element (effects display)
         i.e. one of:

         * hint
         * note
         * warning
         * error

.. rst:directive:: tutorial

   Provides a formatted admonition to make a reader aware of a tutorial
   related to the content they are currently reading.

   For example if we had a tutorial like this:

   .. code-block:: rst

      .. _example-tutorial:

      Example Tutorial
      ----------------

      Meh.

   We could reference it like this:

   .. rst-example::

      .. tutorial:: example-tutorial



"""


__all__ = [
    'Practical',
    'PracticalExtension',
    'Spoiler',
    'setup'
]


from cylc.sphinx_ext.practical.admonitions import (
    Practical,
    PracticalExtension,
    Spoiler,
    Tutorial
)


__version__ = '1.0.0'


def setup(app):
    """Sphinx setup function."""
    from cylc.sphinx_ext import register_static
    app.add_directive('practical', Practical)
    app.add_directive('practical-extension', PracticalExtension)
    app.add_directive('spoiler', Spoiler)
    app.add_directive('tutorial', Tutorial)
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
