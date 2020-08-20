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
'''An extension providing pygments lexers for the Cylc flow.cylc language.


Pygments Lexers
---------------

``cylc``
^^^^^^^^

Lexer for the Cylc language and ``flow.cylc`` extensions.

.. rst-example::

   .. code-block:: cylc

      [scheduling]
          initial cycle point = 2000
          [[dependencies]]
              [[[P1Y]]]
                  graph = """
                      @wall_clock => foo => bar
                      (foo & bar) => pub
                  """

``cylc-graph``
^^^^^^^^^^^^^^

Lexer for the Cylc "graph string" language.

.. rst-example::

   .. code-block:: cylc-graph

      @wall_clock => foo => bar
      (foo & bar) => pub


Domains
-------

Sphinx domain for ``cylc`` configurations.

``cylc``
^^^^^^^^

.. rst-example::

   .. cylc:conf:: my-conf1.cylc

     .. cylc:setting:: foo

        a setting called ``foo``.

        We can use relative references to link to other sections in the
        same configuration tree. Just use ``..`` to back up a level
        like this: :cylc:conf:`[..][bar]pub`

        Note the ``[..]`` will disappear when the docs are built.

        Note also that arbitrary whitespace is supported in references,
        for example :cylc:conf:`[..]
        [bar]
        pub`

     .. cylc:section:: bar

        a section called ``bar``.

        Here's a link to :cylc:conf:`this section <my-conf1.cylc[bar]>`, note
        we re-named the target using the sphinx/rst ``name <target>`` syntax.

        .. cylc:setting:: pub

           a setting called ``pub``

           .. cylc:value:: integer

              :deprecated: 1.2.3

              seconds as an integer.

              the newer :cylc:value:`..=string` is preferred (this is also
              a relative reference).

           .. cylc:value:: string

              an iso8601 duration.


Auto Documenters
----------------

.. rst:directive:: auto-cylc-conf

   Directive for documenting Parsec specification dictionaries.

   .. code-block:: rst

      .. auto-cylc-conf:: name-of-conf python.namespace.SPEC

.. rst:directive:: auto-cylc-type

   Directive for documenting Parsec types.

   Extracts type information from ``cylc.flow``, or, for development purposes,
   from JSON in the directive body.

   .. rst-example::

      .. auto-cylc-type::

         [
             {
                 "name": "boolean",
                 "help": "A boolean in Python format",
                 "options": ["True", "False"],
                 "examples": {
                     "True": "/usr/bin/true to your heart",
                     "False": "oh noes"
                 },
                 "references": [
                     ["rst:dir", "auto-cylc-type"]
                 ]
             }
         ]

      Expected usage would look like this:

      .. code-block:: rst

         .. auto-cylc-type::
            cylc.flow.parsec.validate.ParsecValidator.V_TYPE_HELP
            cylc.flow.parsec.validate.CylcConfigValidator.V_TYPE_HELP


Directives
----------

.. rst:directive:: cylc-scope

   Sets the context for cylc object references.

   .. rst-example::

      .. cylc-scope:: my-conf1.cylc[bar]

      Lets head to the :cylc:conf:`pub`.

   .. rst-example::

      Always be nice and reset the scope afterwards.

      .. cylc-scope::

      .. note::

         This resets it to the hardcoded default which is ``flow.cylc``.

'''

from cylc.sphinx_ext.cylc_lang.autodocumenters import (
    CylcAutoDirective,
    CylcAutoTypeDirective
)
from cylc.sphinx_ext.cylc_lang.domains import (
    ParsecDomain,
    CylcDomain,
    CylcScopeDirective
)
from cylc.sphinx_ext.cylc_lang.lexers import CylcLexer, CylcGraphLexer


__all__ = [
    'CylcAutoDirective',
    'CylcDomain',
    'CylcGraphLexer',
    'CylcLexer',
    'setup'
]

__version__ = '1.0.0'


def setup(app):
    """Sphinx plugin setup function."""
    app.add_lexer('cylc', CylcLexer())
    app.add_lexer('cylc-graph', CylcGraphLexer())
    app.add_domain(CylcDomain)
    app.add_domain(ParsecDomain)
    app.add_directive('auto-cylc-conf', CylcAutoDirective)
    app.add_directive('auto-cylc-type', CylcAutoTypeDirective)
    app.add_directive('cylc-scope', CylcScopeDirective)
    return {'version': __version__, 'parallel_read_safe': True}
