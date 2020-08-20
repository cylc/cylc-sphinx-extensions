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

"""Directive for rendering RST alongside its code representation.

Directives
----------

.. rst:directive:: rst-example

   Display an RST code-snippet followed by its rendering.

   .. directive-seption

   .. rst-example::

      .. rst-example::

          .. note::

             hello world

"""

from .directives import RSTExample

__all__ = ['setup']

__version__ = '1.0.0'


def setup(app):
    app.add_directive('rst-example', RSTExample)
    return {'version': __version__, 'parallel_read_safe': True}
