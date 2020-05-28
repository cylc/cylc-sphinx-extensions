from importlib import import_module
import json
from textwrap import (
    dedent,
    indent
)

from docutils.parsers.rst import Directive
from docutils.statemachine import StringList

from sphinx import addnodes

from cylc.flow.parsec.config import ConfigNode
from cylc.flow.parsec.validate import ParsecValidator, CylcConfigValidator


def get_vdr_info(vdr):
    try:
        return ParsecValidator.V_TYPE_HELP[vdr]
    except KeyError:
        return CylcConfigValidator.V_TYPE_HELP[vdr]


def get_obj_from_module(namespace):
    """Import and return a something from a Python module.

    Examples:
        >>> get_obj_from_module('os')  # doctest: +ELLIPSIS
        <module 'os' from ...>
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
    fields = {}
    if item.vdr:
        vdr_info = get_vdr_info(item.vdr)
        fields['type'] = f':parsec:type:`{vdr_info[0]}`'
    if item.default and item.default != ConfigNode.UNSET:
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
    fields = {}
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


class CylcAutoDirective(Directive):
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
            examples = {k: None for k in examples}
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
        for name, info in sorted(types.items()):
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
