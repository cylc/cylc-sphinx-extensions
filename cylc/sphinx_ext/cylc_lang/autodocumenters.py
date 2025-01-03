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

from copy import copy
from importlib import import_module
import json
import os
from pathlib import Path
from subprocess import run
from textwrap import (
    dedent,
    indent
)
from typing import Any, Dict, List, Optional

from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList, ViewList

from sphinx import addnodes, project
from sphinx.util.docutils import SphinxDirective

from cylc.flow.parsec.config import ConfigNode
from cylc.flow.parsec.validate import ParsecValidator, CylcConfigValidator


CYLC_CONF = 'cylc:conf'


class DependencyError(Exception):
    ...


def get_vdr_info(vdr):
    try:
        return ParsecValidator.V_TYPE_HELP[vdr]
    except KeyError:
        return CylcConfigValidator.V_TYPE_HELP[vdr]


def get_obj_from_module(namespace):
    """Import and return a something from a Python module.

    Examples:
        >>> get_obj_from_module('os')  # doctest: +ELLIPSIS
        <module 'os' ...>
        >>> get_obj_from_module('os.walk')  # doctest: +ELLIPSIS
        <function walk at ...>
        >>> get_obj_from_module('os.path.join')  # doctest: +ELLIPSIS
        <function join at ...>

    """
    head, tail = namespace.split('.'), []
    while head:
        try:
            module = import_module('.'.join(head))
        except ModuleNotFoundError:
            tail.insert(0, head.pop())
        else:
            ret = module
            for item in tail:
                ret = getattr(ret, item)
            return ret


def directive(
    directive,
    arguments=None,
    options=None,
    fields=None,
    content=None
):
    """Write out a RST directive.

    Args:
        directive (str):
            The directive to write.
        arguments (list):
            List of string arguments (cannot contain spaces).
        options (dict):
            Dict of options and values {string: string}.
        fields (dict):
            Dictionary of key-value pairs to prepend as a field
            list to the top of `content`.
        content (str):
            The content of the node as a string.
            Note: this gets stripped and dedented.

    Returns:
        list - List of text lines.

    Examples:
        >>> directive('my_directive', ['a', 'b', 'c'])
        ['.. my_directive:: a b c', '']

    """
    arguments = arguments or []
    ret = [
        f'.. {directive}::{" " if arguments else ""}{" ".join(arguments)}'
    ]
    if options:
        ret.extend([
            f'   :{key}: {value}'
            for key, value in options.items()
        ])
    ret.append('')
    if fields:
        ret.extend([
            f'   :{key}: {value}'
            for key, value in fields.items()
        ])
        ret.append('')
    if content:
        if isinstance(content, List):
            content = '\n'.join(content)
        ret.extend(
            indent(
                # remove indentation and head,tail blanklines
                dedent(content).strip(),
                # add the directive indentation
                '   '
            ).splitlines()
        )
        ret.append('')

    return ret


def repr_value(value):
    """Return a string repr for a configuration value.

    Examples:
        >>> repr_value([1, 3, 5])
        '1, 3, 5'
        >>> repr_value(['a b', 'c d'])
        "'a b', 'c d'"
        >>> repr_value([1, 2, 3])
        '1 .. 3'

    """
    if isinstance(value, list):
        if (
                all((isinstance(x, int) for x in value))
                and value == list(range(value[0], value[-1] + 1))
        ):
            # format range lists nicely (e.g. port ranges)
            return f'{value[0]} .. {value[-1]}'

        # format regular lists being careful to quote where necessary
        return ', '.join((
            f"'{x}'" if ' ' in str(x) else f'{x}'
            for x in value
        ))

    # otherwise just use the string representation
    return str(value)


def doc_setting(item):
    fields = {'Path': f'``{repr(item)}``'}
    parents = list(item.parents())
    if parents and parents[0].meta is True:
        # too meta for us
        # this is a setting in a section in a meta section
        # TODO: this is a limitation which prevents us from documenting
        # deeply nested stuff in meta sections
        return []
    if item.vdr:
        vdr_info = get_vdr_info(item.vdr)
        fields['type'] = f':parsec:type:`{vdr_info[0]}`'
    if item.default not in (None, '', ConfigNode.UNSET):
        fields['default'] = f'``{repr_value(item.default)}``'
    if item.options:
        fields['options'] = ', '.join(
            f'``{option}``'
            if option != ''
            else '`` ``'  # prevents ```` which is an RST error
            for option in item.options
        )

    return directive(
        'cylc:setting',
        [item.display_name],
        {},
        fields,
        item.desc
    )


def doc_section(item):
    fields = {'Path': f'``{repr(item)}``'}
    if item.meta is True:
        # too meta for us
        # this is section inside a meta section
        return []
    if item.meta:
        fields['Inherits'] = f':cylc:conf:`{repr(item.meta)}`'
    return directive(
        'cylc:section',
        [item.display_name],
        {},
        fields,
        item.desc
    )


def doc_conf(item):
    return directive(
        'cylc:conf',
        [item.name],
        {},
        {},
        item.desc
    )


def doc_spec(spec):
    ret = []
    for level, item in spec.walk():
        if level == 0:
            ret.extend(
                doc_conf(item)
            )
        elif item.is_leaf() and not item.meta:
            # setting
            ret.extend([
                indent(line, '   ' * level)
                for line in doc_setting(item)
            ])
        elif not item.is_leaf():
            # section
            ret.extend([
                indent(line, '   ' * level)
                for line in doc_section(item)
            ])
    return ret


    """Auto-documenter for Parsec configuration schemas.

    This implementation translates a Parsec ``SPEC`` into an RST document then
    parses that document.

    Why not extend ``sphinx.ext.autodoc.Documenter``:

    * Looks like these are designed for documenting Python objects not
      documenting configurations which just happen to be defined by Python
      objects.
    * Might be more of an option when we go Python API.

    Why construct an RST document rather doing it programatically:

    * The Cylc Domain relies on nesting to determine structure.
    * Once you run a directive it's already too late to add children.
    * You can bodge it by placing child directives in block quote nodes and
      by hacking the ``ref_context`` passed to the child at run-time
      (at present the Rose equivalent is implement this way)
      but this way feels less hacky as Sphinx is parsing the document
      hierarchically, the way it was intended to be parsed.

    """

    has_content = True
    option_spec = {}
    required_arguments = 1
    optional_arguments = 1

    def run(self):
        if len(self.arguments) == 1:
            spec = get_obj_from_module(self.arguments[0].strip())
        else:
            spec = json.loads('\n'.join(self.content))

        content = doc_spec(spec)

        # parse the RST text
        node = addnodes.desc_content()
        self.state.nested_parse(
            StringList(content),
            self.content_offset,
            node
        )

        return [node]


def doc_type(typ):
    content = []
    if 'help' in typ:
        content.append(dedent(typ['help']).strip())
        content.append('')
    if 'examples' in typ:
        examples = typ['examples']
        content.extend(
            directive('rubric', ['Examples:'])
        )
        if isinstance(examples, list):
            examples = dict.fromkeys(examples)
        for example, notes in examples.items():
            content.append(
                f'* ``{example}``'
                + (f' - {notes}' if notes else '')
            )
        content.append('')
    if 'references' in typ:
        content.extend(
            directive('rubric', ['See Also:'])
        )
        for role, string in typ['references']:
            content.append(
                f'* :{role}:`{string}`'
            )
        content.append('')

    return directive(
        'parsec:type',
        [typ['name']],
        {},
        {},
        '\n'.join(content)
    )


class CylcAutoTypeDirective(Directive):
    """Auto-documenter for Parsec configuration types (i.e. validators)."""

    INFO_FIELDS = [
        'name',
        'help',
        'examples',
        'references'
    ]

    has_content = True
    option_spec = {}
    required_arguments = 0
    optional_arguments = 9

    @classmethod
    def iter_types(cls, objects):
        types = {}
        for obj in objects:
            types.update(obj)
        for _, info in sorted(types.items()):
            yield dict(zip(cls.INFO_FIELDS, info))

    def run(self):
        if len(self.arguments) == 0:
            types = json.loads('\n'.join(self.content))
        else:
            types = self.iter_types([
                get_obj_from_module(arg.strip())
                for arg in self.arguments
            ])

        content = []
        for typ in types:
            content.extend(doc_type(typ))

        node = addnodes.desc_content()
        self.state.nested_parse(
            StringList(content),
            self.content_offset,
            node
        )

        return [node]


class CylcGlobalDirective(SphinxDirective):
    """Represent a Cylc Global Config.
    """
    optional_arguments = 1
    option_spec = {
        'show': directives.split_escaped_whitespace
    }

    def run(self):
        display_these = None
        if 'show' in self.options:
            display_these = [
                i.strip() for i in self.options['show'][0].split(',')]
        src = self.arguments[0] if self.arguments else None
        ret = self.config_to_node(load_cfg(src), src, display_these)
        node = addnodes.desc_content()
        self.state.nested_parse(
            StringList(ret),
            self.content_offset,
            node
        )
        return [node]

    @staticmethod
    def config_to_node(
        config: [Dict, Any],
        src: str,
        display_these=None,
    ) -> List[str]:
        """Take a global config and create a node for display.

        * Displays `platform groups` and then `platforms`.
        * For each group and platform:
            * Adds a title, either the platform name, or the ``[meta]title``
              field.
            * Creates a key item list containing:
                * The name of the item as :regex: if the ``[meta]title`` set.
                * Job Runner.
                * Hosts/Platforms to be selected from.
            * ``[meta]URL``.


        Returns:
            A list of lines for inclusion in the document.
        """
        # Basic info about platforms.
        ret = []

        note = directive(
            'note',
            content=(
                'Platforms and platform groups are listed'
                ' in the order in which Cylc will check for matches to the'
                ' ``[runtime][NAMESPACE]platform`` setting.'
            )
        )

        for section_name, selectable in zip(
            ['platform groups', 'platforms'],
            ['platforms', 'hosts']
        ):
            section = config.get(section_name, {})
            if not section:
                continue

            content = []
            for regex, conf in section.items():
                # Build info about a given platform or platform group.
                section_content = []

                meta = conf.get('meta', {})

                # Title - Use regex if [meta]title not supplied;
                # but include regex field if title is supplied:
                title = meta.get('title', '')
                if title:
                    section_content.append(f':regex: ``{regex}``')
                else:
                    title = regex

                # Job Runner
                section_content.append(
                    f":job runner: {conf.get('job runner', 'background')}")

                # List of hosts or platforms:
                section_content.append(
                    f':{selectable}: ' + ', '.join(
                        f'``{s}``' for s in
                        conf.get(selectable, [regex])
                    )
                )

                # Get [meta]URL - if it exists put it in a seealso directive:
                url = meta.get('URL', '')
                if url:
                    section_content.append(f':URL: {url}')

                # Custom keys:
                section_content += custom_items(meta)

                if display_these:
                    section_content += custom_items(conf, these=display_these)

                # Add description tag.
                description = meta.get('description', '')
                if description:
                    section_content += ['', description, '']

                content += directive(
                    CYLC_CONF, [title], content=section_content)

            ret += directive(
                CYLC_CONF, [section_name], content=content)

        ret = directive(
            CYLC_CONF, [src], content=note + ret)

        # Prettified Debug to help with finding errors:
        if project.logger.getEffectiveLevel() > 9:
            [print(f'{i + 1:03}|{line}') for i, line in enumerate(ret)]

        return ret


class CylcWorkflowDirective(SphinxDirective):
    """Represent a Cylc Workflow Config.
    """
    required_arguments = 1
    option_spec = {
        'show': directives.split_escaped_whitespace
    }

    def run(self):
        display_these = None
        if 'show' in self.options:
            display_these = [
                i.strip() for i in self.options['show'][0].split(',')]
        ret = self.config_to_node(
            load_cfg(self.arguments[0]),
            self.arguments[0],
            display_these
        )
        node = addnodes.desc_content()
        self.state.nested_parse(
            StringList(ret),
            self.content_offset,
            node
        )
        return [node]

    @staticmethod
    def config_to_node(config, src, display_these=None):
        """Document Workflow

        Additional processing:
        * If no title field is provided use either the workflow folder
          or the task/family name.

        """
        workflow_content = []

        # Handle workflow level metadata:
        workflow_meta = config.get('meta', {})
        # Title or path
        workflow_name = workflow_meta.get('title', '')
        if not workflow_name:
            workflow_name = src
        
        # URL if available
        url = workflow_meta.get('URL', '')
        if url:
            workflow_content += directive('seealso', [url])

            # Custom keys:
            workflow_content += custom_items(workflow_meta)

        # Description:
        workflow_content += ['', workflow_meta.get('description', ''), '']

        # Add details of the runtime section:
        for task_name, taskdef in config.get('runtime', {}).items():
            task_content = []
            task_meta = taskdef.get('meta', {})

            # Does task have a title?
            title = task_meta.get('title', '')
            if title:
                title = f'{title} ({task_name})'
            else:
                title = task_name

            # Task URL
            url = task_meta.get('URL', '')
            if url:
                task_content.append(f':URL: {url}')

            # Custom keys:
            task_content += custom_items(task_meta)

            # Config keys given
            if display_these:
                task_content += custom_items(taskdef, display_these)

            desc = task_meta.get('description', '')
            if desc:
                task_content += ['', desc, '']

            workflow_content += directive(
                CYLC_CONF, [title], content=task_content)

        ret = directive(CYLC_CONF, [workflow_name], content=workflow_content)

        # Pretty debug statement:
        if project.logger.getEffectiveLevel() > 9:
            [print(f'{i + 1:03}|{line}') for i, line in enumerate(ret)]

        return ret


def load_cfg(conf_path: Optional[str] = None) -> Dict[str, Any]:
    """Get Workflow Configuration metadata:

    Args:
        conf_path: global or workflow conf path.

    Raises:
        DependencyError: If a version of Cylc without the
            ``cylc config --json`` facility is installed.
    """
    env = None
    if conf_path is None:
        cmd = ['cylc', 'config', '--json']
    elif (Path(conf_path) / 'flow.cylc').exists():
        # Load workflow Config:
        cmd = ['cylc', 'config', '--json', conf_path]
    elif (Path(conf_path) / 'flow/global.cylc').exists():
        # Load Global Config:
        if conf_path:
            env = copy(os.environ)
            env = env.update({'CYLC_SITE_CONF_PATH': conf_path})
            cmd = ['cylc', 'config', '--json']
    else:
        raise FileNotFoundError(
            f'No Cylc config file found at {conf_path}')

    sub = run(
        cmd,
        capture_output=True,
        env=env or os.environ
    )

    # Catches failure caused by a version of Cylc without
    # the ``cylc config --json`` option.
    if sub.returncode:
        # cylc config --json not available:
        if 'no such option: --json' in sub.stderr.decode():
            msg = (
                'Requires cylc config --json, not available'
                ' for this version of Cylc')
            raise DependencyError(msg)
        # all other errors in the subprocess:
        else:
            msg = 'Cylc config metadata failed with: \n'
            msg += '\n'.join(
                i.strip("\n") for i in sub.stderr.decode().split('\n'))
            raise Exception(msg)

    return json.loads(sub.stdout)


def custom_items(
    data: Dict[str, Any],
    not_these: Optional[List[str]] = None,
    these: Optional[List[str]] = None
) -> List[str]:
    """Given a dict return a keylist.

    Args:
        data: The input dictionary.
        not_these: Keys to ignore.
        these: Keys to include.

    Examples:
        >>> data = {'foo': 'I cannot believe it!', 'title': 'Hi'}
        >>> custom_items(data)
        :foo:
           I cannot believe it!
        >>> custom(data, these=['title'])
        :title:
           Hi
    """
    ret = []
    if these:
        for key in these:
            value = data.get(key, '')
            if value and isinstance(value, str):
                value = value.replace("\n", "\n   ")
                ret.append(f':{key}:\n   {value}')
    else:
        for key, val in data.items():
            if (
                key not in (not_these or ['title', 'description', 'URL'])
                and isinstance(val, str)
            ):
                value = val.replace("\n", "\n   ")
                ret.append(f':{key}:\n   {value}')
    return ret
