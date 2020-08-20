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
"""An extension for visualising simple Cylc graph strings.

.. rst-example::

   .. minicylc::
      :snippet:

      foo => bar => baz

Directives
----------

.. _graphviz size attribute: https://graphviz.org/doc/info/attrs.html#d:size

.. rst:directive:: minicylc

   Renders a visualisation of a simple Cylc graph.

   In HTML documents this will display an animated graph,
   otherwise a plain graph will be displayed as an image.

   .. rst:directive:option:: snippet
      :type: flag

      If set a code snippet containing the graph string will also be rendered.

   .. rst:directive:option:: size

      Sets the `graphviz size attribute`_.

   .. rst:directive:option:: theme

      The name of the colour theme for animation, currently supported:

      demo
          Active / completed tasks are blue, all other states are blank.
      default
          Classic Cylc7 theme.

   .. note::

      Inherits options from the :rst:dir:`digraph` directive.

Configuration
-------------

Required
^^^^^^^^

extensions
   Must include ``sphinx.ext.graphviz``
graphviz_output_format
   Must be set to ``svg`` for animated visualisations

Recommended
^^^^^^^^^^^

extensions
    Should contain either:

    * ``sphinxcontrib.rsvgconverter``
    * ``sphinxcontrib.inkscapeconverter``

graphviz_dot_args
    ``['-Gfontname=sans', '-Nfontname=sans', '-Gbgcolor=none']``

"""


from cylc.sphinx_ext.minicylc.minicylc import MiniCylc, MiniCylcDirective

from sphinx.ext.graphviz import (
    latex_visit_graphviz,
    texinfo_visit_graphviz,
    text_visit_graphviz,
    man_visit_graphviz
)


__all__ = ['MiniCylc', 'MiniCylcDirective', 'setup']

__version__ = '1.0.0'


def setup(app):
    """Sphinx plugin setup function."""
    from cylc.sphinx_ext import register_static
    app.add_node(MiniCylc,
                 html=(MiniCylc.visit_html, None),
                 latex=(latex_visit_graphviz, None),
                 texinfo=(texinfo_visit_graphviz, None),
                 text=(text_visit_graphviz, None),
                 man=(man_visit_graphviz, None))
    app.add_directive('minicylc', MiniCylcDirective)
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
