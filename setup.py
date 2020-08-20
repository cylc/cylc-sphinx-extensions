#!/usr/bin/env python3
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
import re

from pathlib import Path

from setuptools import find_namespace_packages, setup


def get_version(filename):
    """Read __version__ from filename."""
    with open(filename, 'r') as src_file:
        return re.search(
            r'__version__.*=[\s+]?[\'\"](.*)[\'\"]',
            src_file.read()
        ).groups()[0]


__version__ = get_version(
    Path('cylc/sphinx_ext/__init__.py')
)


TESTS_REQUIRE = [
    'pytest'
]


REQS = {
    'cylc_lang': [
        'pygments',
        'cylc-flow'
    ],
    'hieroglyph_addons': [
        'hieroglyph'
    ],
    'rtd_theme_addons': [
        'sphinx_rtd_theme'
    ],
    'sub_lang': [
        'pygments'
    ],
    'test': [
        'pycodestyle'
    ]
}
REQS['all'] = list(
    {x for y in REQS.values() for x in y}
    | set(TESTS_REQUIRE)
)


setup(
    name='cylc-sphinx-extensions',
    version=__version__,
    license='GPL',
    license_file='LICENCE',
    description='Sphinx extensions for documenting Cylc',
    long_description=open('README.rst', 'r').read(),
    install_requires=[
        'sphinx>=2',
    ],
    tests_require=TESTS_REQUIRE,
    extras_require=REQS,
    packages=find_namespace_packages(include=["cylc.*"]),
    package_data={
        'cylc.sphinx_ext': [
            '*/_static/*/*'
        ]
    }
)
