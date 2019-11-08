import logging
import re

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


KEYS = {
    'conf': lambda s: f'{s}',
    'section': lambda l: ''.join(f'[{s}]' for s in l),
    'setting': lambda s: s,
    'value': lambda s: f'={s}'
}

CYLC_WORD = r'''
    (?:[\w\-\_])?
    (?:[\w\-\_][\w\-\_ \.]+)?
    [\w]
'''

REGEX = re.compile(
    rf'''
    ^
    # the base configuration
    (?:
        (?P<conf>{CYLC_WORD})
        # must be followed by a section or setting
        (?=[\[\|])
    )?
    # the sections
    (?:
        (?:
            # regex cannot capture an arbitrary number of sections
            # so we define a "max depth" here
            (?:\[(?P<section1>{CYLC_WORD})\])?
            (?:\[(?P<section2>{CYLC_WORD})\])?
            (?:\[(?P<section3>{CYLC_WORD})\])?
        )|(?:
            \|
        )
    )?
    # the setting
    (?P<setting>{CYLC_WORD})?
    # the value
    (?:
        (?:\s+)?=(?:\s+)?
        (?P<value>.*)
    )?
    $
    ''',
    re.X
)


def tokenise(namespace_string):
    """Convert a namespace string into a list of token tuples.

    Examples:
        Normal Usage:
        >>> tokenise('a = b')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': None,
         'section': None,
         'setting': 'a',
         'value': 'b'}
        >>> tokenise('x[a][b][c]d = e')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': 'x',
         'section': ('a', 'b', 'c'),
         'setting': 'd',
         'value': 'e'}
        >>> tokenise('x|a')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': 'x',
         'section': None,
         'setting': 'a',
         'value': None}

        Edge Cases:
        >>> tokenise('-a b')['setting']
        '-a b'
        >>> tokenise('a= c=d')['value']
        'c=d'
        >>> tokenise('__MANY__')['setting']
        '__MANY__'

        Exceptions:
        >>> tokenise('a b ')
        Traceback (most recent call last):
        ValueError: Not a valid namespace "a b "
        >>> tokenise(' a b')
        Traceback (most recent call last):
        ValueError: Not a valid namespace " a b"

    """
    match = REGEX.match(namespace_string)
    if match:
        ret = match.groupdict()
        ret['section'] = tuple((
            value
            for key, value in ret.items()
            if 'section' in key
            if value is not None
        )) or None
        return {
            key: ret[key]
            for key in KEYS
        }
    raise ValueError(f'Not a valid namespace "{namespace_string}"')


def detokenise(namespace_tokens):
    """
    Examples:
        >>> detokenise(tokenise('x[a][b][c]d=e'))
        'x[a][b][c]d=e'
        >>> detokenise(tokenise('x|a'))
        'x|a'
        >>> detokenise(tokenise('a'))
        'a'

    """
    ret = ''
    for key, fmt in KEYS.items():
        value = namespace_tokens.get(key)
        if value:
            if (
                    key == 'setting'
                    and namespace_tokens.get('conf')
                    and not namespace_tokens.get('section')
            ):
                ret += '|'
            ret += fmt(value)
    return ret


def partials_from_tokens(tokens):
    """
    Examples:
        >>> partials_from_tokens(  # doctest: +NORMALIZE_WHITESPACE
        ...     tokenise('x[a][b][c]d=e'))
        (('conf', 'x'),
         ('section', ('a', 'b', 'c')),
         ('setting', 'd'),
         ('value', 'e'))
        >>> partials_from_tokens(  # doctest: +NORMALIZE_WHITESPACE
        ...     tokenise('a'))
        (('setting', 'a'),)

    """
    return tuple((
        (key, value)
        for key, value in tokens.items()
        if value
    ))


def tokens_from_partials(partials):
    """
    Examples:
        >>> tokens_from_partials([  # doctest: +NORMALIZE_WHITESPACE
        ...     ('conf', 'a'),
        ...     ('section', 'b'),
        ...     ('section', 'c'),
        ...     ('setting', 'd')
        ... ])
        {'conf': 'a',
         'section': ('b', 'c'),
         'setting': 'd',
         'value': None}

    """
    ret = {}
    for key in KEYS:
        if key == 'section':
            ret[key] = []
        else:
            ret[key] = None
        for partial in list(partials):
            partial_key, partial_value = partial
            if partial_key == key:
                if key == 'section':
                    ret[key].append(partial_value)
                else:
                    ret[key] = partial_value
        if key == 'section':
            ret[key] = tuple(ret[key])
    return ret


class CylcDirective(ObjectDescription):

    NAME = None

    def run(self):
        self.ref_context_key = self.get_reference_context()

        index_node, cont_node = ObjectDescription.run(self)

        # cont_node.ref_context = {
        #     self.ref_context_key: None
        # }

        return [index_node, cont_node]

    def before_content(self):
        # add ref_context_key variable
        self.state.document.settings.env.ref_context[self.ref_context_key] = (
            id(self)
        )
        ObjectDescription.before_content(self)

    def after_content(self):
        # remove ref_context_key variable
        self.state.document.settings.env.ref_context.pop(self.ref_context_key)
        ObjectDescription.after_content(self)

    @classmethod
    def sanitise_signature(cls, sig):
        """
        Examples:
            >>> CylcSettingDirective.sanitise_signature('a=b')
            'a', 'b'

        """
        value = None
        if cls.NAME == 'setting':
            tokens = tokenise(sig)
            value = tokens['value']
            tokens['value'] = None
            sig = detokenise(tokens)
        return sig, value

    def handle_signature(self, sig, signode):
        sig, value = self.sanitise_signature(sig)
        signode += addnodes.desc_name(sig, sig)
        if value:
            annotation = f' = {value}'
            signode += addnodes.desc_annotation(annotation, annotation)
        return (sig, self.NAME, sig)

    def get_tokens(self, sig):
        return tokens_from_partials(
            [
                # extract tokens from the ref_context
                (context[1], context[2])
                for context
                in self.state.document.settings.env.ref_context
                if isinstance(context, tuple)
                and context[0] == 'cylc'
            ] + [
                # include this node
                (sig[1], sig[2])
            ]
        )

    def add_target_and_index(self, sig, _, signode):
        tokens = self.get_tokens(sig)
        tokens['value'] = None
        # register this item with the cylc domain
        self.env.domains['cylc'].set(tokens, self.env.docname)
        # associate this node with the fqdn (allows hyperlinks)
        signode['ids'].append(detokenise(tokens))

    def get_index_text(self, modname, name):
        return ''  # TODO?

    def get_reference_context(self):
        name = self.arguments[0].strip()
        return ('cylc', self.NAME, name, id(self))


class CylcConfDirective(CylcDirective):

    NAME = 'conf'


class CylcSectionDirective(CylcDirective):

    NAME = 'section'


class CylcSettingDirective(CylcDirective):

    NAME = 'setting'


class CylcValueDirective(CylcDirective):

    NAME = 'value'


class CylcXRefRole(XRefRole):
    """Handle references to Rose objects.

    This should be minimal."""

    def process_link(self, env, refnode, has_explicit_title, title, target):
        # copy ref_context to the refnode so that we can access it in
        # resolve_xref. Note that walking through the node tree to extract
        # ref_context items appears only to work in the HTML buider.
        refnode['ref_context'] = dict(env.ref_context)
        # target = target.replace('<', '').replace('>', '')
        print('%', title, target)
        return title, target


class CylcDomain(Domain):

    name = 'cylc'
    """Prefix for the Cylc Domain (used by Sphinx)."""

    label = 'Cylc'
    """Display label (used by Sphinx)."""

    object_types = {
        'conf': ObjType('conf', 'conf', 'obj'),
        'section': ObjType('section', 'section', 'obj'),
        'setting': ObjType('setting', 'setting', 'obj'),
        'value': ObjType('value', 'value', 'obj')
    }
    """List of object types, these should mirror the ``directives``."""

    directives = {
        'conf': CylcConfDirective,
        'section': CylcSectionDirective,
        'setting': CylcSettingDirective,
        'value': CylcSettingDirective
    }
    """Associate domain prefixes with the directives used to define them."""

    roles = {
        'conf': CylcXRefRole(),
        'section': CylcXRefRole(),
        'setting': CylcXRefRole(),
        'value': CylcXRefRole()
    }
    """The RST text "roles" associated with the domain ``:cylc:<role>:``."""

    initial_data = {
        # all registered cylc stuff should have an entry in this dictionary
        'objects': {}
    }
    """This sets ``self.data`` on initialisation."""

    def clear_doc(self, docname):
        """Wipe all entries for the specified docname."""
        for partials, x_docname in self.data['objects'].items():
            if docname == x_docname:
                self.data['objects'].pop(partials)

    def get(self, tokens):
        partials = partials_from_tokens(tokens)
        return self.data['objects'][partials]

    def set(self, tokens, docname):
        partials = partials_from_tokens(tokens)
        self.data['objects'][partials] = docname

    def get_objects(self):
        for partials, docname in self.data['objects'].items():
            tokens = tokens_from_partials(partials)
            name = detokenise(tokens)
            dispname = name
            for type_ in reversed(list(KEYS)):
                if type_ in tokens and tokens[type_]:
                    break
            anchor = name
            priority = 1
            yield(
                name,
                dispname,
                type_,
                docname,
                anchor,
                priority
            )

    def resolve_xref(
        self, env, fromdocname, builder, typ, target, node, contnode):
        if typ == 'conf':
            tokens = {'conf': target}
        else:
            tokens = tokenise(target)
            tokens.pop('value')

        try:
            docname = self.get(tokens)
        except KeyError:
            # object does not exist, "nitpicky" mode will pick this up
            import pdb; pdb.set_trace()
            return None

        display = detokenise(tokens)  # .replace('<', '').replace('>', '')

        return make_refnode(
            builder,
            fromdocname,
            docname,
            display,
            contnode,
            display
        )
