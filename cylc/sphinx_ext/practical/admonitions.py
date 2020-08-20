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
"""An extension providing a directive for writing pratical sections."""

from docutils import nodes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.statemachine import StringList


class Practical(BaseAdmonition):
    """Directive for practical sections in documentation.

    This class serves as a stand-in for maintainability purposes. It is
    equivalent to:

        .. admonition:: Practical
           :class: note

    """
    node_class = nodes.admonition
    NAME = 'Practical'
    CLASSES = ['note']

    def run(self):
        self.options.update({'class': self.CLASSES})  # Affects the display.
        self.arguments = [self.NAME]  # Sets the title of the admonition.
        return super(Practical, self).run()


class PracticalExtension(Practical):
    """Directive for practical extension exercises."""
    NAME = 'Practical Extension'
    CLASSES = ['note', 'spoiler']


class Spoiler(BaseAdmonition):
    """Directive for auto-hidden "spoiler" sections.

    When rendered in HTML the section will be collapsed and a "Show" button put
    in its place.

    Otherwise the content will be displayed normally.

    """
    node_class = nodes.admonition
    required_arguments = 1

    def run(self):
        classes = ['spoiler']
        args = self.arguments[0].split(' ')
        if len(args) > 1:
            classes.append(args[1])
        self.arguments = args[:1]
        self.options.update({'class': classes})
        return super(Spoiler, self).run()


class Tutorial(BaseAdmonition):
    """Directive for referencing a tutorial in related content.

    This class serves as a stand-in for maintainability purposes. It is
    equivalent to:

        .. admonition:: Tutorial
           :class: note

    """
    node_class = nodes.admonition
    NAME = 'Related Tutorial'
    CLASSES = ['tip', 'tutorial-ref']
    required_arguments = 1
    has_content = False

    def run(self):
        self.options.update({'class': self.CLASSES})  # Affects the display.
        self.content = StringList([f':ref:`{self.arguments[0]}`'])
        self.arguments = [self.NAME]  # Sets the title of the admonition.
        return super(Tutorial, self).run()
