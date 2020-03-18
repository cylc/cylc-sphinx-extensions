from importlib import import_module
import json

from docutils.parsers.rst import Directive
from docutils.statemachine import StringList

from sphinx import addnodes
from sphinx.directives import ObjectDescription

from cylc.flow.parsec.validate import ParsecValidator, CylcConfigValidator
from cylc.sphinx_ext.cylc_lang.domains import (
    CylcConfDirective,
    CylcSectionDirective,
    CylcSettingDirective,
    CylcValueDirective
)


def get_vdr_info(vdr):
    try:
        return ParsecValidator.V_TYPE_HELP[vdr]
    except KeyError:
        return CylcConfigValidator.V_TYPE_HELP[vdr]


def get_obj_from_module(namespace):
    """
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


class CylcAutoTypeDirective(Directive):

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

    @staticmethod
    def doc_type(info, directive_arguments):
        content = []
        if 'help' in info:
            content.append(info['help'])
        if 'examples' in info:
            examples = info['examples']
            content.append('')
            content.append('.. rubric:: Examples:')
            content.append('')
            if isinstance(examples, list):
                examples = {k: None for k in examples}
            for example, notes in examples.items():
                content.append(
                    f'* ``{example}``'
                    + (f' - *{notes}*' if notes else '')
                )
        if 'references' in info:
            content.append('')
            content.append('.. rubric:: See Also:')
            content.append('')
            for role, string in info['references']:
                content.append(
                    f'* :{role}:`{string}`'
                )

        return ObjectDescription(
            'describe',
            [info['name']],
            {},
            StringList(content),
            *directive_arguments
        ).run()

    def run(self):
        if len(self.arguments) == 0:
            types = json.loads('\n'.join(self.content))
        else:
            types = self.iter_types([
                get_obj_from_module(arg.strip())
                for arg in self.arguments
            ])

        directive_arguments = (
            self.lineno,
            self.content_offset,
            self.block_text,
            self.state,
            self.state_machine
        )

        nodes = []
        for info in types:
            nodes.extend(
                self.doc_type(info, directive_arguments)
            )
        return nodes


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

    @staticmethod
    def doc_conf(name):
        return [
            f'.. cylc:conf:: {name}',
            ''
        ]

    @staticmethod
    def doc_section(name):
        return [
            f'.. cylc:section:: {name}',
            ''
        ]

    @staticmethod
    def doc_setting(name, vdr, default=None, *options):
        ret = [
            f'.. cylc:setting:: {name}',
            ''
        ]
        vdr_info = get_vdr_info(vdr)
        if vdr:
            # TODO - link the type back to the parsec defn
            ret.append(f'   :type: {vdr_info[0]}')
        if default:
            ret.append(f'   :default: {default}')
        if options:
            options = ', '.join((f'``{option}``' for option in options))
            ret.append(f'   :options: {options}')
        ret.append('')
        return ret

    @classmethod
    def doc_spec(cls, spec, partials):
        ret = []
        for key, value in spec.items():
            if isinstance(value, dict):
                # section
                ret.extend(
                    cls.doc_section(key)
                )
                section_partials = partials + [('section', key)]
                ret.extend([
                    f'   {line}'
                    for line in cls.doc_spec(value, section_partials)
                ])
            elif isinstance(value, list):
                # setting
                ret.extend(
                    cls.doc_setting(key, *value)
                )
            else:
                raise TypeError(value)
        return ret

    def run(self):
        conf_name = self.arguments[0].strip()
        if len(self.arguments) == 2:
            spec = get_obj_from_module(self.arguments[1].strip())
        else:
            spec = json.loads('\n'.join(self.content))

        content = []

        # document the top-level configuration
        content.extend(
            self.doc_conf(conf_name)
        )

        # document the SPEC
        content.extend([
            f'   {line}'
            for line in self.doc_spec(spec, [('conf', conf_name)])
        ])

        # parse the RST text
        node = addnodes.desc_content()
        self.state.nested_parse(
            StringList(content),
            self.content_offset,
            node
        )

        return [node]
