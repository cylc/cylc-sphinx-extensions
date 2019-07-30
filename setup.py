#!/usr/bin/env python3
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

from pathlib import Path
import re
from setuptools import setup, find_packages


def get_version(filename):
    """Read __version__ from filename."""
    with open(filename, 'r') as src_file:
        return re.search(
            r'__version__.*=[\s+]?[\'\"](.*)[\'\"]',
            src_file.read()
        ).groups()[0]


__version__ = get_version(
    Path('cylc/sphinx/__init__.py')
)


install_requires = {
    'all': [
        'sphinx'
    ],
    'cylc_lang': [
        'pygments'
    ],
    'sub_lang': [
        'pygments'
    ]
}


setup(
    name='cylc-sphinx-extensions',
    version=__version__,
    description='Sphinx extensions for documenting Cylc',
    long_description=open('README.rst', 'r').read(),
    long_description_content_type='text/x-rst',
    install_requires=list({x for y in install_requires.values() for x in y}),
    extras_require={
        'test': {'pycodestyle'}
    },
    packages=find_packages()
)
