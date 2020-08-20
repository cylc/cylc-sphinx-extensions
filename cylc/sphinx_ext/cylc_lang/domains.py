import re

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import make_refnode


DEFAULT_SCOPE = 'flow.cylc'

KEYS = {
    'conf': lambda s: f'{s}',
    'section': lambda l: ''.join(f'[{s}]' for s in l),
    'setting': lambda s: s,
    'value': lambda s: f'={s}'
}

# NOTE we allow `<...>` because this is used for custom sections
# (i.e. for `__MANY__` items)
CYLC_WORD = r'''
    (?:[\<\w\-\_])?
    (?:[\w\-\_][\w\-\_ ]+)?
    [\w\>]
'''

REGEX = re.compile(
    rf'''
    ^
    # the base configuration
    (?:
        (?P<conf>[\w\-\_]+\.[\w]+)
    )?
    # the sections
    (?:
        (?:
            # regex cannot capture an arbitrary number of sections
            # so we define a "max depth" here
            (?:\[(?P<section1>(?:(?:{CYLC_WORD})|(?:\.\.)))\])?
            (?:\s+)?  # allow arbitrary whitespace
            (?:\[(?P<section2>(?:(?:{CYLC_WORD})|(?:\.\.)))\])?
            (?:\s+)?  # allow arbitrary whitespace
            (?:\[(?P<section3>(?:(?:{CYLC_WORD})|(?:\.\.)))\])?
            (?:\s+)?  # allow arbitrary whitespace
            (?:\[(?P<section4>(?:(?:{CYLC_WORD})|(?:\.\.)))\])?
            # note \.\. is to allow relative referencing
        )|(?:
            \|
        )
    )?
    # the setting
    (?:\s+)?  # allow arbitrary whitespace
    (?P<setting>(?:(?:{CYLC_WORD})|\.\.))?
    # the value (note \.\. is to allow relative referencing)
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
        >>> tokenise('x.cylc')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': 'x.cylc',
         'section': None,
         'setting': None,
         'value': None}
        >>> tokenise('a = b')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': None,
         'section': None,
         'setting': 'a',
         'value': 'b'}
        >>> tokenise('x.cylc[a][b][c]d = e')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': 'x.cylc',
         'section': ('a', 'b', 'c'),
         'setting': 'd',
         'value': 'e'}
        >>> tokenise('x.cylc|a')  # doctest: +NORMALIZE_WHITESPACE
        {'conf': 'x.cylc',
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

        Permitted Arbitrary Whitesapce:
        >>> tokenise(' [a] [b] [c] ')['section']
        ('a', 'b', 'c')
        >>> tokenise(' [a] b ')['setting']
        'b'

        Exceptions:
        >>> tokenise('a[b]c[d]')
        Traceback (most recent call last):
        ValueError: Not a valid namespace "a[b]c[d]"

    """
    namespace_string = namespace_string.strip()
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
        Full namespace
        >>> detokenise(tokenise('x.cylc[a][b][c]d=e'))
        'x.cylc[a][b][c]d=e'
        >>> detokenise(tokenise('x.cylc|a'))
        'x.cylc|a'
        >>> detokenise(tokenise('x.cylc'))
        'x.cylc'
        >>> detokenise(tokenise('a'))
        'a'

        Partial namespace
        >>> detokenise({'section': 'a'})
        '[a]'

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
        ...     tokenise('x.cylc[a][b][c]d=e'))
        (('conf', 'x.cylc'),
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
        ...     ('conf', 'a.cylc'),
        ...     ('section', ('b', 'c')),
        ...     ('setting', 'd')
        ... ])
        {'conf': 'a.cylc',
         'section': ('b', 'c'),
         'setting': 'd',
         'value': None}
        >>> tokens_from_partials([  # doctest: +NORMALIZE_WHITESPACE
        ...     ('section', ('a',)),
        ... ])
        {'conf': None,
         'section': ('a',),
         'setting': None,
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
                    ret[key].extend(partial_value)
                else:
                    ret[key] = partial_value
        if key == 'section':
            ret[key] = tuple(ret[key])
    return ret


def tokens_relative(base, override):
    """Return one pat h relative to the other.

    Arguments:
        base (dict):
            Tokens dictionary, the absolute path.
        override (dict):
            Tokens dictionary, the relative path.

    Returns:
        dict - Token dictionary.

    Examples:
        >>> def test_tokens(base, override):
        ...     return detokenise(tokens_relative(
        ...         tokenise(base), tokenise(override)))

        >>> test_tokens('a.cylc[b]c', '[..]d')
        'a.cylc[b]d'
        >>> test_tokens('a.cylc[b]c=d', '..=e')
        'a.cylc[b]c=e'
        >>> test_tokens('a.cylc[b]c', '[..][d]e')
        'a.cylc[b][d]e'
        >>> test_tokens('a.cylc[b]', '[c]d')
        'a.cylc[b][c]d'
        >>> test_tokens('a.cylc[b]c=d', '[..][..]e')
        'a.cylc[b]e'

    """
    # ensure that base is an aboslute path
    if not base.get('conf'):
        return ValueError(f'{base} is not an absoute path')

    # if override is an absolute path return it (cannot make it relative)
    if override.get('conf'):
        return override

    base_list = []
    over_list = []
    for token in KEYS:
        base_value = base.get(token)
        over_value = override.get(token)
        if token == 'section':
            if base_value:
                base_list.extend(base_value)
            if over_value:
                over_list.extend(over_value)
        else:
            if base_value:
                base_list.append(base_value)
            if over_value:
                over_list.append(over_value)

    path = base_list + over_list

    kill = []
    run = None
    for ind, item in enumerate(list(path)):
        if run is not None and item == '..':
            run = ind
            kill.extend([ind, ind - 3])
        elif item == '..':
            run = ind
            kill.extend([ind, ind - 1])
        else:
            run = None

    for ind in sorted([x for x in kill if x > 0], reverse=True):
        del path[ind]

    tokens = {key: None for key in KEYS}
    tokens['conf'] = path.pop(0)
    if override.get('value') is not None:
        tokens['value'] = path.pop()
    if override.get('setting') is not None:
        tokens['setting'] = path.pop()
    tokens['section'] = tuple(path)

    return tokens


class CylcDirective(ObjectDescription):

    NAME = None

    def run(self):
        self.ref_context_key = self.get_reference_context()

        index_node, cont_node = ObjectDescription.run(self)

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
            ('a', 'b')

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
        signode += addnodes.desc_name(sig, self.display_name())
        if value:
            annotation = f' = {value}'
            signode += addnodes.desc_annotation(annotation, annotation)
        return (sig, self.NAME, sig)

    def display_name(self):
        sig = self.arguments[0]
        if self.NAME == CylcSectionDirective.NAME:
            sig = [sig]
        return detokenise({self.NAME: sig})

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
                (sig[1], (sig[2],)) if self.NAME == 'section'
                else (sig[1], sig[2])
            ]
        )

    def add_target_and_index(self, sig, _, signode):
        tokens = self.get_tokens(sig)
        if self.NAME != 'value':
            tokens['value'] = None
        # register this item with the cylc domain
        self.env.domains['cylc'].set(tokens, self.env.docname)
        # associate this node with the fqdn (allows hyperlinks)
        signode['ids'].append(detokenise(tokens))

    def get_index_text(self, modname, name):
        return ''  # TODO?

    def get_reference_context(self):
        # name = self.arguments[0].strip()
        name, _ = self.sanitise_signature(self.arguments[0].strip())
        if self.NAME == 'section':
            name = (name,)
        return ('cylc', self.NAME, name, id(self))


class CylcConfDirective(CylcDirective):

    NAME = 'conf'


class CylcSectionDirective(CylcDirective):

    NAME = 'section'


class CylcSettingDirective(CylcDirective):

    NAME = 'setting'


class CylcValueDirective(CylcDirective):

    NAME = 'value'


class CylcScopeDirective(SphinxDirective):
    """Sets the namespace for relative references.

    Example:
        See the :cylc:conf:`x[a]b` setting

        .. cylc-scope: x[a]

        See the :cylc:conf:`b` setting.

        Be nice and tidy up afterwards:

        .. cylc:scope::

        Done.

    """

    # effectively permits spaces in arguments
    optional_arguments = 99

    @staticmethod
    def get_ref_context(namespace):
        """
            >>> CylcScopeDirective.get_ref_context('a.cylc[b][c]d'
            ... )  # doctest: +NORMALIZE_WHITESPACE
            [('cylc', 'conf', 'a.cylc', None),
            ('cylc', 'section', ('b', 'c'), None),
            ('cylc', 'setting', 'd', None)]

            >>> CylcScopeDirective.get_ref_context('a.cylc')
            [('cylc', 'conf', 'a.cylc', None)]
        """
        ret = []
        for token, value in partials_from_tokens(tokenise(namespace)):
            ret.append(('cylc', token, value, None))
        return ret

    @staticmethod
    def wipe_scope(ref_context):
        for item in dict(ref_context):
            if isinstance(item, tuple) and item[0] == 'cylc':
                ref_context.pop(item)

    def run(self):
        scope = DEFAULT_SCOPE
        if len(self.arguments) >= 1:
            scope = ' '.join(self.arguments)
        self.wipe_scope(self.env.ref_context)
        for partials in self.get_ref_context(scope):
            self.env.ref_context[partials] = None
        return []


class CylcXRefRole(XRefRole):
    """Handle references to Rose objects.

    This should be minimal."""

    def process_link(self, env, refnode, has_explicit_title, title, target):
        # copy ref_context to the refnode so that we can access it in
        # resolve_xref. Note that walking through the node tree to extract
        # ref_context items appears only to work in the HTML buider.
        # refnode['ref_context'] = dict(env.ref_context)
        refnode['ref_context'] = tuple((
            (context[1], context[2])
            for context, _ in env.ref_context.items()
            if isinstance(context, tuple)
            and context[0] == 'cylc'
        ))  # TODO combine
        return (
            # standardise namespace (this removes arbitrary whitespace)
            detokenise(tokenise(
                title
                # strip newlines just from the reference
                # (sphinx seems to handle this separately for the domain)
                .replace('\n', '')
                # strip relative syntax
                .replace('[..]', '')
                .replace('..', '')
            )),
            target
        )


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
        'value': CylcValueDirective
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
        for partials, x_docname in list(self.data['objects'].items()):
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
        self, env, fromdocname, builder, typ, target, node, contnode
    ):
        # strip intersphinx mapping
        # TODO

        # allow line breaks in long references
        target = target.replace('\n', ' ')

        # get tokens for the object we are trying to reference
        tokens = tokenise(target)

        # get the context of the reference (the scope)
        ref_tokens = None
        if not tokens['conf']:
            ref_tokens = tokens_from_partials(node['ref_context'])
            if not any(ref_tokens.values()):
                ref_tokens = tokenise(DEFAULT_SCOPE)
            tokens = tokens_relative(ref_tokens, tokens)

        # get the page this item is documented on
        try:
            try:
                # have a go at getting the setting with a value if specified
                docname = self.get(tokens)
            except KeyError:
                # if we can't find it, drop the value and try again
                # this allows stuff like this:
                #  > will work if you set :cylc:conf:`foo = 1`.
                # otherwise we would have to document the value ``1``
                tokens['value'] = None
                docname = self.get(tokens)
        except KeyError:
            # object does not exist, "nitpicky" mode will pick this up
            # context = detokenise(ref_tokens)
            message = (
                f'Could not reference "{detokenise(tokens)}"'
                f' from the context'
                f' "{detokenise(ref_tokens or tokenise(DEFAULT_SCOPE))}"'
                f' in file "{fromdocname}".'
            )
            import sys
            print(message, sys.stderr)
            return None

        # standardise the display text
        display = detokenise(tokens)

        # build and return a reference node
        return make_refnode(
            builder,
            fromdocname,
            docname,
            display,
            contnode,
            display
        )


# The following is a minimal domain for documenting parsec objects.
# Sadly the standard domain is not suitable for documenting these things
# because it's entries are not linkable so we need an new domain

def parsec_ref(tokens):
    """The detokenise equivalent for parsec (much simpler).i

    Example:
        >>> parsec_ref(('domain_name', 'object_type', 'object name'))
        'domain_name-object_type-object_name'

    """
    return ('-'.join(tokens)).replace(' ', '_')


class ParsecDirective(ObjectDescription):
    """Base directive for parsec objects."""

    DOMAIN = 'parsec'
    TYP = None

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        return sig

    def add_target_and_index(self, sig, _, signode):
        tokens = (self.DOMAIN, self.TYP, sig)
        # register this item with the cylc domain
        self.env.domains[self.DOMAIN].set(tokens, self.env.docname)
        # associate this node with the fqdn (allows hyperlinks)
        signode['ids'].append(parsec_ref(tokens))


class ParsecTypeDirective(ParsecDirective):
    """Directive for parsec "types" i.e. validators."""

    TYP = 'type'


class ParsecDomain(Domain):
    """Domain for documenting primitive parsec objects.

    This way they become referenceable objects we can link to from other
    sections. This "domain" is a minimal facade to achieve this.

    """

    name = 'parsec'
    label = 'Parsec'

    object_types = {
        'type': ObjType('type', 'type', 'obj')
    }

    directives = {
        'type': ParsecTypeDirective
    }

    roles = {
        'type': XRefRole()
    }

    initial_data = {
        'objects': {}
    }

    dangling_warnings = {
    }

    def set(self, tokens, docname):
        self.data['objects'][tokens] = docname

    def get(self, tokens):
        return self.data['objects'][tokens]

    def get_objects(self):
        for tokens, docname in self.data['objects'].items():
            name = tokens[-1]
            dispname = name
            anchor = name
            priority = 1
            yield(
                name,
                dispname,
                'type',
                docname,
                anchor,
                priority
            )

    def resolve_xref(
        self, env, fromdocname, builder, typ, target, node, contnode
    ):
        tokens = ('parsec', typ, target)

        # get the page this item is documented on
        try:
            docname = self.get(tokens)
        except KeyError:
            # object does not exist, "nitpicky" mode will pick this up
            return None

        # detokenise
        display = parsec_ref(tokens)

        # build and return a reference node
        return make_refnode(
            builder,
            fromdocname,
            docname,
            display,
            contnode,
            display
        )
