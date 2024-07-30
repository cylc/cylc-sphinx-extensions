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
import os
from pathlib import Path
from docutils import nodes
from typing import Dict, List, Optional
from sphinx.util.docutils import SphinxDirective
from cylc.flow.config import WorkflowConfig
from cylc.flow.cfgspec.glbl_cfg import glbl_cfg
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles


rawdoc = """An extension for grabbing Cylc Config Metadata.

.. rst-example::

   .. cylc_metadata::
      :source: {workflow_path}

   .. cylc_metadata::
      :global: {workflow_path}


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

workflow_path = Path(__file__).parent.parent.parent.parent / 'etc'
__doc__ = rawdoc.format(workflow_path=workflow_path)
__all__ = ['CylcMetadata', 'setup']
__version__ = '1.0.0'


def setup(app):
    """Sphinx plugin setup function."""
    app.add_directive('cylc_metadata', CylcMetadata)

    return {'version': __version__, 'parallel_read_safe': True}


class Doc(ViewList):
    """Convenience wrapper for ViewList to allow us to use it to
    collect lines of RST, with options to underline."""
    def append(self, text: str, underline: Optional[str] = None):
        super().append(text, '', 1)
        if underline:
            super().append(underline * len(text), '', 1)
        super().append('', '', 1)


class CylcMetadata(SphinxDirective):
    """Represent a Cylc Config.

    .. cylc_metadata::

    .. TODO::

       - Template variable and opt conf keys support
    """
    optional_arguments = 3

    def run(self):
        # Parse input options:
        for key, value in zip(
            [i.strip(':') for i in self.arguments[::2]],
            list(self.arguments[1::2])
        ):
            self.options.update({key: value})

        # Get global or workflow metadara
        if 'global' in self.options:
            metadata = self.get_global_metadata(self.options['global'])
            rst = self.convert_global_to_rst(metadata)
        else:
            metadata = self.get_workflow_metadata(self.options['source'])
            rst = self.convert_workflow_to_rst(metadata)

        container = nodes.Element()
        nested_parse_with_titles(self.state, rst, container)
        return container.children

    @staticmethod
    def get_metadata(cfg, keys: Optional[List[str]] = None):
        """Get metadata items from a config.

        Args:
            keys: Keys to access metadata - if given this is
                assumed to be a section containing sections contining
                metadata. This is a reasonable assumption
                for current Cylc configs but may need reviewing.

        Returns:
            A metadata dictionary.
        """
        meta = {}
        if keys:
            for section, content in cfg.get(keys).items():
                meta[section] = content['meta']
        else:
            meta = cfg.get(['meta'])
        return meta

    @staticmethod
    def get_global_metadata(conf_path: str) -> Dict[str, Dict[str, str]]:
        """Get Global Configuration metadata:

        Args:
            Path: Global conf path.

        Additional Processing:
        * Get lists of hosts/platforms and job runner from the config.
        * If no title is provided, use the platform/group regex as the title.
        * If title != regex then insert text saying which regex
          needs matching to select this platform.

        Returns:
            A dictionary in the form:
            'platforms': {'platform regex': {..metadata..}},
            'platform groups': {'platform regex': {..metadata..}}

        TODO - Reliably load from conf path
        """
        # Load Global Config:
        os.environ['CYLC_SITE_CONF_PATH'] = conf_path
        from cylc.flow.cfgspec import global
        config = glbl_cfg(cached=)
        # delattr(config, '_DEFAULT')
        # config = glbl_cfg()

        # extract metadata
        metadata = {}
        for section in ['platforms', 'platform groups']:
            metadata[section] = CylcMetadata.get_metadata(config, [section])
            for key in config.get([section]).keys():
                # Grab a list of hosts or platforms that this
                # platform or group will select from:
                select_from = (
                    config.get([section, key]).get('hosts')
                    or config.get([section, key]).get('platforms'))
                select_from = select_from or [key]
                metadata[section][key]['select_from'] = select_from

                # Grab the job runner this platform uses:
                if section == 'platforms':
                    metadata[section][key]['job_runner'] = config.get(
                        [section, key]).get('job runner', 'background')
        return metadata

    @staticmethod
    def convert_global_to_rst(meta):
        """Convert the global metadata into rst format."""
        rst = Doc()
        rst.append('Global Config', '#')
        rst.append('.. note::')
        rst.append(
            '   platforms and platform groups are listed in the order in which'
            ' Cylc will check for matches to the'
            ' ``[runtime][NAMESPACE]platform`` setting.')
        for settings, selects in zip(
            ['platform groups', 'platforms'], ['platforms', 'hosts']
        ):
            if meta.get(settings, {}):
                rst.append(settings, '=')
                for regex, info in reversed(meta[settings].items()):
                    title = info.get('title', '')
                    if not title:
                        title = regex
                    rst.append(title, '^')
                    if title != regex:
                        rst.append(
                            f'match ``{regex}`` to select these {settings}.')
                    rst.append(info.get('description', 'No description'))

                    if info.get('job_runner'):
                        rst.append(
                            'This platform uses job runner'
                            f' ``{info.get("job_runner")}``')

                    rst.append(f'Selects {selects} from:')
                    for selectable in info['select_from']:
                        rst.append(f'* ``{selectable}``')
        return rst

    @staticmethod
    def get_workflow_metadata(conf_path: str) -> Dict[str, Dict[str, str]]:
        """Get workflow metadata.

        Additional processing:
        * If no title foeld is provided use either the workflow folder
          or the task/family name.
        * Don't return the root family if there is no metadata.

        Returns:
            'workflow': {.. top level metadata ..},
            'runtime': {'namespace': '.. task or family metadata ..'}

        """
        # Load Workflow Config
        config = WorkflowConfig(
            '', os.path.join(conf_path, 'flow.cylc'), {}, {})
        # Extract Data
        meta = {}
        meta['workflow'] = CylcMetadata.get_metadata(config.pcfg)
        meta['runtime'] = CylcMetadata.get_metadata(config.pcfg, ['runtime'])

        # Title is parent directory if otherwise unset:
        if not meta['workflow'].get('title', ''):
            meta['workflow']['title'] = Path(conf_path).name

        # Title of namespace is parent if otherwise unset:
        poproot = False
        for namespace, info in meta['runtime'].items():
            # don't display root unless it's actually had some
            # metadata added, but save a flag rather than modifying
            # the iterable being looped over:
            if (
                namespace == 'root'
                and not any(meta['runtime'].get('root').values())
            ):
                poproot = True

            if not info.get('title', ''):
                meta['runtime'][namespace]['title'] = namespace

        if poproot:
            meta['runtime'].pop('root')

        return meta

    @staticmethod
    def convert_workflow_to_rst(meta):
        rst = Doc()

        # Handle the workflow config metadata:
        workflow = meta['workflow']
        rst.append(workflow.get('title'), '#')
        rst.append(workflow.get('description', 'No description given'))

        # Handle the runtime config metadata:
        rst.append('Runtime', '=')
        for taskmeta in meta['runtime'].values():
            rst.append(taskmeta['title'], '^')
            rst.append(taskmeta['description'])

        return rst
