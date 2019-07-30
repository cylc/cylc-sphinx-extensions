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
from cylc.sphinx import __version__

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

    # cylc.sphinx extensions
    'cylc.sphinx.cylc_lang',
    'cylc.sphinx.diff_selection',
    'cylc.sphinx.grid_table',
    'cylc.sphinx.hieroglyph_theme_addons',
    'cylc.sphinx.minicylc',
    'cylc.sphinx.practical',
    'cylc.sphinx.rtd_theme_addons',
    'cylc.sphinx.sub_lang',

    # addons required by extensions
    'hieroglyph',
    'sphinx_rtd_theme',
]

# minicylc settings
graphviz_output_format = 'svg'
