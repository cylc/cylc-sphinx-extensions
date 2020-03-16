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
"""Monkey patch hieroglyph to work with Sphinx 1.8.0+.

.. _Hieroglyph issue: https://github.com/nyergler/hieroglyph/issues/148

This extension serves as a temporary workaround, for more information see
`Hieroglyph issue`_.

If an extension provides its own visit or depart methods, patch them into the
``HTMLTranslator`` class below.

It would be possible to patch the ``add_node`` method of the Sphinx application
to patch extensions automatically but in the interests of keeping the hack to a
minimum this hard-coded extension should suffice.

.. note::

   extension is automatically loaded when added to extensions, no directives or
   configurations required.


"""

import sphinx

from sphinx.writers.html import HTMLTranslator

from sphinx.ext.graphviz import html_visit_graphviz
from sphinx.ext.autosummary import (autosummary_toc_visit_html,
                                    autosummary_table_visit_html)
from cylc.sphinx_ext.minicylc import MiniCylc


__version__ = '1.0.0'


def none(*args, **kwargs):
    pass


def setup(app):
    if tuple(int(x) for x in sphinx.__version__.split('.')) > (1, 7, 9):
        # sphinx.ext.graphviz
        HTMLTranslator.visit_graphviz = html_visit_graphviz

        # sphinx.ext.autosummary
        HTMLTranslator.visit_autosummary_toc = autosummary_toc_visit_html
        HTMLTranslator.depart_autosummary_toc = none
        HTMLTranslator.visit_autosummary_table = autosummary_table_visit_html
        HTMLTranslator.depart_autosummary_table = none

        # ext.minicylc
        HTMLTranslator.visit_MiniCylc = MiniCylc.visit_html
    return {'version': __version__, 'parallel_read_safe': True}
