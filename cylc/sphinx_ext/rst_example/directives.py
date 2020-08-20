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

from sphinx import addnodes
from sphinx.directives.code import CodeBlock
from sphinx.util.docutils import SphinxDirective


class RSTExample(SphinxDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0

    def run(self):
        node = addnodes.desc_content()
        self.state.nested_parse(
            self.content,
            self.content_offset,
            node
        )

        return [
            CodeBlock(
                self.name,
                ['rst'],
                {},
                self.content,
                self.lineno,
                self.content_offset,
                self.block_text,
                self.state,
                self.state_machine
            ).run()[0],
            node
        ]
