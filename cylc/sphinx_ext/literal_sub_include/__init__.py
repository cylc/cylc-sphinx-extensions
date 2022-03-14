# -----------------------------------------------------------------------------
# THIS FILE IS PART OF THE CYLC WORKFLOW ENGINE.
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
"""A literal include block that supports hardcoded substitutions.

.. note::

   Hopefully we can move a feature like this into Sphinx in the long run.


Directives
----------

.. rst:directive:: literalsubinclude

   Directive for practical exercise.

   .. rst-example::

      With substitutions turned off:

      .. literalsubinclude:: ../cylc/sphinx_ext/literal_sub_include/test.txt

      With substitutions turned on:

      .. literalsubinclude:: ../cylc/sphinx_ext/literal_sub_include/test.txt
        :substitutions:

Configurations
--------------


.. object:: literal_sub_include_subs

   Dictionary containing key value pairs of substitutions e.g::

      literal_sub_include_subs = {
          'version': '123',
      }

.. note::

   Patching into the Sphinx substitutions appears to be tricky due to the
   stage at which they are applied.

"""

from typing import TYPE_CHECKING

from cylc.sphinx_ext.literal_sub_include.directives import LiteralSubInclude

if TYPE_CHECKING:
    from sphinx.application import Sphinx


__version__ = '1.0.0'


def setup(app: "Sphinx"):
    app.add_directive('literalsubinclude', LiteralSubInclude)
    app.add_config_value('literal_sub_include_subs', {}, 'env', 'dict')
    return {'version': __version__, 'parallel_read_safe': True}
