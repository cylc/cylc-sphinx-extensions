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
import json
from sphinx.util.docutils import SphinxDirective
# from cylc.flow.config import WorkflowConfig
# from cylc.flow.cfgspec.glbl_cfg import glbl_cfg
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
from subprocess import run


rawdoc = """An extension for grabbing Cylc Config Metadata.

.. rst-example::

   .. cylc_metadata::
      :global: {workflow_path}

   .. cylc_metadata::
      :source: {workflow_path}


Directives
----------

.. rst:directive:: cylc_metadata

   Get a Cylc Configuration and render it.

   .. rst:directive:option:: source
      :type: string

      If set, renders the metadata of a workflow, otherwise the global
      config.

   .. rst:directive:option:: global
      :type: string

      Set CYLC_SITE_CONF_PATH to this value.

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
    def append(self, text, underline=None):
        super().append(text, '', 1)
        if underline:
            super().append(underline * len(text), '', 1)
        super().append('', '', 1)


class CylcMetadata(SphinxDirective):
    """Represent a Cylc Config.
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
        if 'source' in self.options:
            config = self.load_workflow_cfg(self.options['source'])
            metadata = self.get_workflow_metadata(
                config, self.options['source'])
            rst = self.convert_workflow_to_rst(metadata)
        else:
            config = self.load_global_cfg(self.options['global'])
            metadata = self.get_global_metadata(config)
            rst = self.convert_global_to_rst(metadata)

        container = nodes.Element()
        nested_parse_with_titles(self.state, rst, container)
        return container.children

    @staticmethod
    def load_global_cfg(conf_path=None):
        """Get Global Configuration metadata:

        Args:
            Path: Global conf path.

        """
        # Load Global Config:
        if conf_path:
            env = os.environ
            sub = run(
                ['cylc', 'config', '--json'],
                capture_output=True,
                env=env.update({'CYLC_SITE_CONF_PATH': conf_path})
            )
        else:
            sub = run(['cylc', 'config', '--json'], capture_output=True)
        return json.loads(sub.stdout)

    @staticmethod
    def get_global_metadata(config):
        """
        Additional Processing:
        * Get lists of hosts/platforms and job runner from the config.
        * If no title is provided, use the platform/group regex as the title.
        * If title != regex then insert text saying which regex
          needs matching to select this platform.

        Returns:
            A dictionary in the form:
            'platforms': {'platform regex': {..metadata..}},
            'platform groups': {'platform regex': {..metadata..}}
        """
        metadata = {}
        for section, select_from in zip(
            ['platforms', 'platform groups'],
            ['hosts', 'platforms']
        ):
            metadata[section] = config.get(section)
            if not metadata[section]:
                continue
            for key in config.get(section).keys():
                # Grab a list of hosts or platforms that this
                # platform or group will select from:
                select_from = (
                    config.get(section).get(key).get('hosts')
                    or config.get(section).get(key).get('platforms'))
                select_from = select_from or [key]
                metadata[section][key]['select_from'] = select_from

                # Grab the job runner this platform uses:
                if section == 'platforms':
                    metadata[section][key]['job_runner'] = config.get(
                        section).get(key).get('job runner', 'background')
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
    def load_workflow_cfg(conf_path):
        """Get Workflow Configuration metadata:

        Args:
            conf_path: workflow conf path.
        """
        # Load Global Config:
        sub = run(
            ['cylc', 'config', '--json', conf_path],
            capture_output=True,
        )
        return json.loads(sub.stdout)

    @staticmethod
    def get_workflow_metadata(config, conf_path):
        """Get workflow metadata.

        Additional processing:
        * If no title field is provided use either the workflow folder
          or the task/family name.
        * Don't return the root family if there is no metadata.

        Returns:
            'workflow': {.. top level metadata ..},
            'runtime': {'namespace': '.. task or family metadata ..'}

        """
        # Extract Data
        meta = {}

        # Copy metadata to the two top level sections:
        meta['workflow'] = config.get('meta')
        meta['runtime'] = {
            k: v.get('meta', {})
            for k, v in config.get('runtime', {}).items()}

        # Title is parent directory if otherwise unset:
        if not meta.get('workflow', {}).get('title', ''):
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

            # If metadata doesn't have a title set title to the namespace name:
            if not info.get('title', ''):
                meta['runtime'][namespace]['title'] = namespace

        if poproot:
            meta['runtime'].pop('root')

        return meta

    @staticmethod
    def convert_workflow_to_rst(meta):
        """Convert workflow metadata to RST.

        Returns
        """
        rst = Doc()

        # Handle the workflow config metadata:
        CylcMetadata.write_section(rst, meta.get('workflow', {}), '#')

        # Handle the runtime config metadata:
        rst.append('Runtime', '=')
        for taskmeta in meta['runtime'].values():
            CylcMetadata.write_section(rst, taskmeta)

        return rst

    @staticmethod
    def write_section(rst, section, title_level='^'):
        # Title
        title = section.get('title', '')
        if not title:
            return
        rst.append(title, title_level)

        # Url
        url = section.get('url', '')
        if url:
            rst.append(url)

        # Description
        rst.append(section.get('description', ''))
