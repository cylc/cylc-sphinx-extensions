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
"""An extension providing a pygments lexer for <substitutions> in text.

.. rubric:: Examples

Pygments language: ``sub``

.. code-block:: rst

   .. code-block:: sub

      # foo
      bar <pub>

.. code-block:: sub

   # foo
   bar <pub>

"""


from cylc.sphinx_ext.sub_lang.lexer import SubstitutionLexer


__all__ = ['SubstitutionLexer', 'setup']

__version__ = '1.0.0'


def setup(app):
    """Sphinx plugin setup function."""
    app.add_lexer('sub', SubstitutionLexer())
    return {'version': __version__, 'parallel_read_safe': True}
