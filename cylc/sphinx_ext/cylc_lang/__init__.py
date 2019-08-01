# -----------------------------------------------------------------------------
# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2019 NIWA & British Crown (Met Office) & Contributors.
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
'''An extension providing pygments lexers for the Cylc suite.rc language.

.. rubric:: Examples

Pygments language: `cylc`

.. code-block:: rst

   .. code-block:: cylc

      [scheduling]
          initial cycle point = 2000
          [[dependencies]]
              [[[P1Y]]]
                  graph = """
                      @wall_clock => foo => bar
                      (foo & bar) => pub
                  """

.. code-block:: cylc

   [scheduling]
       initial cycle point = 2000
       [[dependencies]]
           [[[P1Y]]]
               graph = """
                   @wall_clock => foo => bar
                   (foo & bar) => pub
               """

Pygments language: `cylc-graph`

.. code-block:: rst

   .. code-block:: cylc-graph

      @wall_clock => foo => bar
      (foo & bar) => pub

.. code-block:: cylc-graph

   @wall_clock => foo => bar
   (foo & bar) => pub

'''

from cylc.sphinx_ext.cylc_lang.lexers import CylcLexer, CylcGraphLexer


__all__ = ['CylcLexer', 'CylcGraphLexer', 'setup']

__version__ = '1.0.0'


def setup(app):
    """Sphinx plugin setup function."""
    app.add_lexer('cylc', CylcLexer())
    app.add_lexer('cylc-graph', CylcGraphLexer())
    return {'version': __version__, 'parallel_read_safe': True}
