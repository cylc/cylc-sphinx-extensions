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
from cylc.sphinx_ext import __version__

# project settings
master_doc = 'index'
project = 'Cylc Sphinx Extensions'
release = __version__
html_theme = 'sphinx_rtd_theme'
extensions = [
    # sphinx built-in extensions
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.graphviz',
    'sphinx.ext.intersphinx',

    # cylc.sphinx_ext extensions
    'cylc.sphinx_ext.cylc_lang',
    'cylc.sphinx_ext.diff_selection',
    'cylc.sphinx_ext.grid_table',
    'cylc.sphinx_ext.hieroglyph_addons',
    'cylc.sphinx_ext.hieroglyph_patch',
    'cylc.sphinx_ext.minicylc',
    'cylc.sphinx_ext.practical',
    'cylc.sphinx_ext.rtd_theme_addons',
    'cylc.sphinx_ext.rst_example',
    'cylc.sphinx_ext.sub_lang',

    # addons required by extensions
    'hieroglyph',
    'sphinx_rtd_theme',
]

# minicylc settings
graphviz_output_format = 'svg'
graphviz_dot_args = ['-Gfontname=sans', '-Nfontname=sans', '-Gbgcolor=none']

# autosummary options
templates_path = ['_templates']
autosummary_generate = True
autosummary_imported_members = True

# external references
intersphinx_mapping = {
    'sphinx': ('http://www.sphinx-doc.org/', None)
}
