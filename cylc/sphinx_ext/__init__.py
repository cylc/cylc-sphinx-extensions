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
"""Sphinx extensions for documenting Cylc projects."""


from pathlib import Path
import os


__version__ = '1.1.0'


def register_static(app, extension):
    """Register the _static directory of an extension.

    Args:
        app (Sphinx.App):
            The sphinx application (as provided in the first argument of
            the Sphinx ``setup()`` function.
        extension (str):
            The name of the Sphinx extension i.e. ``__name__``.

    """
    app.config.html_static_path.append(
        str(
            Path(__file__).resolve().parent.joinpath(
                extension.replace(__name__ + '.', '').replace('.', os.sep),
                '_static'
            )
        )
    )
