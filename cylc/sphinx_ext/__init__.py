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
"""Sphinx extensions for documenting Cylc projects."""


from pathlib import Path
import os
from shutil import copyfile


__version__ = '1.2.0'


# map sub directory name to the name of the sphinx registration function
# which should be called to include the static resource
STATIC_BINDINGS = [
    # (sub_dir, name_of_registration_function)
    ('css', 'add_css_file'),
    ('js', 'add_js_file')
]


def get_static_file_installer(static_files):
    """Return an installer for the provided list of static files.

    This installs static files into the Sphinx builder's _static
    directory.

    Arguments:
        static_files (list):
            List of (absolute_path: Path, relative_path: Path) items.

    Returns:
        callable - Hook function for Sphinx to run.

    """
    def _install(app):
        nonlocal static_files
        try:
            outdir = app.builder.outdir
            assert outdir
        except (AttributeError, AssertionError):
            breakpoint()
        dest_static_path = Path(outdir, '_static')
        for abs_path, rel_path in static_files:
            dest = dest_static_path / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            copyfile(abs_path, dest)
    return _install


def register_static(app, extension):
    """Register the _static directory of an extension.

    Args:
        app (Sphinx.App):
            The sphinx application (as provided in the first argument of
            the Sphinx ``setup()`` function.
        extension (str):
            The name of the Sphinx extension i.e. ``__name__``.

    """
    src_static_path = Path(__file__).resolve().parent.joinpath(
        extension.replace(__name__ + '.', '').replace('.', os.sep),
        '_static'
    )
    assert src_static_path.exists()

    # get list of static files to install
    static_files = []
    for sub_dir, fcn_name in STATIC_BINDINGS:
        static_dir = (src_static_path / sub_dir)
        registation_fcn = None
        if fcn_name:
            registation_fcn = getattr(app, fcn_name)
        if static_dir.exists():
            for abs_path in static_dir.iterdir():
                rel_path = abs_path.relative_to(src_static_path)
                if abs_path.is_file():
                    static_files.append((abs_path, rel_path))
                if registation_fcn:
                    registation_fcn(str(rel_path))

    # add an installer function as a hook to be run once the builder has
    # initiated
    app.connect('builder-inited', get_static_file_installer(static_files))
