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
"""An extension for grabbing Cylc Config Metadata.

.. rst-example::

   .. cylc_metadata::
      :source: /home/h02/tpilling/metomi/cylc-sphinx-extensions/extensions/flow.cylc

   .. cylc_metadata::
      :global: /home/h02/tpilling/metomi/cylc-sphinx-extensions/extensions


Directives
----------

.. rst:directive:: cylc_metadata

   Get a Cylc Configuration and render it.

   .. rst:directive:option:: source
      :type: string

      If set, renders the metadata of a workflow, otherwise the global
      config.

   .. rst:directive:option:: CYLC_CONF_PATH
      :type: string

      If set, override the CYLC_SITE_CONF_PATH. Only
      relevent if loading a global config

   .. rst:directive:option:: render_empty
      :type: boolean

      If true renders empty metadata values.

"""

__all__ = ['CylcMetadata', 'setup']

__version__ = '1.0.0'

import os

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from docutils.parsers.rst import directives
from pathlib import Path
from cylc.flow.config import WorkflowConfig
from cylc.flow.cfgspec.glbl_cfg import glbl_cfg
from sphinx.directives.other import Include
from docutils import io, nodes, statemachine, utils
from sphinx.directives.code import CodeBlock
from sphinx import addnodes
from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles



def setup(app):
    """Sphinx plugin setup function."""
    app.add_directive('cylc_metadata', CylcMetadata)

    return {'version': __version__, 'parallel_read_safe': True}


class CylcMetadata(SphinxDirective):
    """Represent a Cylc Config.

    .. cylc_metadata::

    .. TODO::

       - Template variable and opt conf keys support
    """
    optional_arguments = 3

    def run(self):
        for key, value in zip(
            [i.strip(':') for i in self.arguments[::2]],
            [i for i in self.arguments[1::2]]
        ):
            self.options.update({key: value})

        print(self.options)
        if 'source' in self.options:
            config = WorkflowConfig(
                '',
                self.arguments[1],
                {},
                {}
            )
            is_global = False
        else:
            config = glbl_cfg(cached=False)
            config.USER_CONF_PATH = self.options['global']
            config = config.get_inst()
            is_global = True
        metadata = config.get_metadata()

        rst = self.convert_to_rst(metadata, is_global)

        # Add the content one line at a time.
        # Second argument is the filename to report in any warnings
        # or errors, third argument is the line number.

        # Create a node.
        node = nodes.section()
        node.document = self.state.document

        # Parse the rst.
        nested_parse_with_titles(self.state, rst, node)

        # And return the result.
        return node.children

    def convert_to_rst(self, meta, is_global):
        if is_global:
            return self.convert_global_to_rst(meta)
        return self.convert_workflow_to_rst(meta)

    @staticmethod
    def convert_global_to_rst(meta):
        rst = ViewList()
        rst.append('NotImplementedError', '', 1)
        return rst

    @staticmethod
    def convert_workflow_to_rst(meta):
        rst = ViewList()
        rst.append(f'# garbage', '', 1)
        return rst
