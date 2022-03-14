# -----------------------------------------------------------------------------
# THIS FILE IS PART OF THE CYLC WORKFLOW ENGINE.
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

from functools import wraps
from typing import List

from docutils.parsers.rst import directives
from sphinx.directives.code import LiteralInclude, LiteralIncludeReader


def substitute(lines: List[str], items: dict) -> None:
    """Substitute |strings| in the provided "lines" with values from "items".

    Example:
        >>> lines = ['foo |bar| baz', 'foo bar |baz|']
        >>> substitute(lines, {'bar': 'pub', 'baz': 'qux'})
        >>> lines
        ['foo pub baz', 'foo bar qux']
    """
    for ind, line in enumerate(lines):
        for key, value in items.items():
            line = line.replace(f'|{key}|', value)
        lines[ind] = line


def substitution_decorator(fcn):
    """Decorator for LiteralIncludeReader adding substitution functionality."""
    @wraps(fcn)
    def _inner(self, *args, **kwargs):
        nonlocal fcn
        lines = fcn(self, *args, **kwargs)
        if 'substitutions' in self.options:
            # perform substitutions
            substitute(
                lines,
                self.options['_config'].literal_sub_include_subs,
            )
        return lines
    return _inner


# patch the LiteralIncludeReader class
LiteralIncludeReader.read_file = substitution_decorator(
    LiteralIncludeReader.read_file
)


class LiteralSubInclude(LiteralInclude):
    # add an option to turn on subs
    option_spec = {
        **LiteralInclude.option_spec,
        'substitutions': directives.flag,
    }

    def run(self):
        # pass the config through to the LiteralIncludeReader
        self.options['_config'] = self.config
        return LiteralInclude.run(self)
