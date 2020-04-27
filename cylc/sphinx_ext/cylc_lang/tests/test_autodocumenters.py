import pytest

from cylc.flow.parsec.config import ConfigNode
from cylc.flow.parsec.validate import ParsecValidator as VDR

from cylc.sphinx_ext.cylc_lang.autodocumenters import (
    directive,
    doc_conf,
    doc_section,
    doc_setting,
    doc_spec,
    doc_type
)


def test_directive():
    """It should return RST directives."""
    assert directive(
        'directive-name',
        ['arg1', 'arg2', 'arg3'],
        {'opt1': 'foo', 'opt2': 'bar'},
        {'field1': 'baz', 'field2': 'pub'},
        '''
            foo
            bar
            baz
        '''
    ) == [
        '.. directive-name:: arg1 arg2 arg3',
        '   :opt1: foo',
        '   :opt2: bar',
        '',
        '   :field1: baz',
        '   :field2: pub',
        '',
        '   foo',
        '   bar',
        '   baz',
        ''
    ]

    # nothing
    assert directive(
        'directive-name',
        [], {}, {}, ''
    ) == [
        '.. directive-name::',
        ''
    ]

    # no args
    assert directive(
        'directive-name',
        [],
        {'opt1': 'foo'},
        {'field1': 'baz'},
        'content'
    ) == [
        '.. directive-name::',
        '   :opt1: foo',
        '',
        '   :field1: baz',
        '',
        '   content',
        ''
    ]

    # no opts
    assert directive(
        'directive-name',
        ['arg1'],
        {},
        {'field1': 'baz'},
        'content'
    ) == [
        '.. directive-name:: arg1',
        '',
        '   :field1: baz',
        '',
        '   content',
        ''
    ]

    # no fields
    assert directive(
        'directive-name',
        ['arg1', 'arg2', 'arg3'],
        {'opt1': 'foo'},
        {},
        'content'
    ) == [
        '.. directive-name:: arg1 arg2 arg3',
        '   :opt1: foo',
        '',
        '   content',
        ''
    ]

    # no content
    assert directive(
        'directive-name',
        ['arg1', 'arg2', 'arg3'],
        {'opt1': 'foo'},
        {},
        ''
    ) == [
        '.. directive-name:: arg1 arg2 arg3',
        '   :opt1: foo',
        ''
    ]


@pytest.fixture
def simple_setting():
    """A leaf-node configuration."""
    return ConfigNode('simple-setting', VDR.V_STRING)


@pytest.fixture
def option_setting():
    """A leaf-node configuration with options."""
    return ConfigNode('option-setting', VDR.V_STRING, options=['a', 'b', 'c'])


@pytest.fixture
def default_setting():
    """A leaf-node configuration with a default."""
    return ConfigNode('default-setting', VDR.V_STRING, default='x')


@pytest.fixture
def documented_setting():
    """A leaf-node configuration with documentation."""
    return ConfigNode('documented-setting', VDR.V_STRING, desc='''
        foo
        bar
        baz
    ''')


def test_doc_setting(
        simple_setting,
        option_setting,
        default_setting,
        documented_setting
):
    """It should document leaf-node configurations."""
    assert doc_setting(simple_setting) == [
        '.. cylc:setting:: simple-setting',
        '',
        '   :type: :parsec:type:`string`',
        ''
    ]

    assert doc_setting(option_setting) == [
        '.. cylc:setting:: option-setting',
        '',
        '   :type: :parsec:type:`string`',
        '   :options: ``a``, ``b``, ``c``',
        ''
    ]

    assert doc_setting(default_setting) == [
        '.. cylc:setting:: default-setting',
        '',
        '   :type: :parsec:type:`string`',
        '   :default: ``x``',
        ''
    ]

    assert doc_setting(documented_setting) == [
        '.. cylc:setting:: documented-setting',
        '',
        '   :type: :parsec:type:`string`',
        '',
        '   foo',
        '   bar',
        '   baz',
        ''
    ]


@pytest.fixture
def simple_section():
    """A configuration section."""
    return ConfigNode('simple-section')


def test_doc_section(simple_section):
    """It should docuement configuration sections."""
    assert doc_section(simple_section) == [
        '.. cylc:section:: simple-section',
        ''
    ]


@pytest.fixture
def simple_conf():
    """A root configuration."""
    return ConfigNode('simple-conf')


@pytest.fixture
def documented_conf():
    """A root configuration with documentation."""
    return ConfigNode('documented-conf', desc='''
        foo
        bar
        baz
    ''')


def test_doc_conf(simple_conf, documented_conf):
    """It should document top-level configuration items."""
    assert doc_conf(simple_conf) == [
        '.. cylc:conf:: simple-conf',
        ''
    ]

    assert doc_conf(documented_conf) == [
        '.. cylc:conf:: documented-conf',
        '',
        '   foo',
        '   bar',
        '   baz',
        ''
    ]


@pytest.fixture
def documented_spec():
    """A configuration tree with documentation."""
    with ConfigNode('documented-conf', desc='a\nb\nc') as spec:
        with ConfigNode('documented-section', desc='d\ne'):
            ConfigNode('documented-setting', VDR.V_STRING, desc='f\ng')
    return spec


def test_doc_spec(documented_spec):
    """It should document entire configuration trees."""
    assert doc_spec(documented_spec) == [
        '.. cylc:conf:: documented-conf',
        '',
        '   a',
        '   b',
        '   c',
        '',
        '   .. cylc:section:: documented-section',
        '',
        '      d',
        '      e',
        '',
        '      .. cylc:setting:: documented-setting',
        '',
        '         :type: :parsec:type:`string`',
        '',
        '         f',
        '         g',
        ''
    ]


@pytest.fixture
def basic_parsec_type():
    return {
        'name': 'type name',
        'help': '''
            help
            string
        ''',
        'examples': ['a', 'b', 'c'],
        'references': [('foo', 'FOO'), ('bar', 'BAR')]
    }


def test_doc_type(basic_parsec_type):
    assert doc_type(basic_parsec_type) == [
        '.. parsec:type:: type name',
        '',
        '   help',
        '   string',
        '',
        '   .. rubric:: Examples:',
        '',
        '   * ``a``',
        '   * ``b``',
        '   * ``c``',
        '',
        '   .. rubric:: See Also:',
        '',
        '   * :foo:`FOO`',
        '   * :bar:`BAR`',
        '',

    ]
