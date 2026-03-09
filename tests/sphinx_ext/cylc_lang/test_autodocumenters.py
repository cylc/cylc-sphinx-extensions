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
# ----------------------

import pytest
from types import SimpleNamespace

from cylc.sphinx_ext.cylc_lang.autodocumenters import (
    CylcWorkflowDirective,
    CylcGlobalDirective,
    DependencyError,
    _handle_cylc_config_returncode,
    _pick_config_file,
    custom_items,
    load_cfg,
)


param = pytest.param


FLOWFILE = 'flow.cylc'
GLOBALFILE = 'flow/global.cylc'


def test_pick_config_file_none():
    """It returns a default command if no conf path given."""
    assert _pick_config_file(None) == ('cylc config --json'.split(), None)


def test_pick_config_file_flow_cylc(tmp_path):
    """It returns a workflow specific command if a workflow location is given.
    """
    (tmp_path / FLOWFILE).touch()
    assert _pick_config_file(str(tmp_path)) == (
        f'cylc config --json {tmp_path}'.split(), None)


def test_pick_config_file_global_cylc(tmp_path):
    """It returns a default command AND an environment containing
    CYLC_SITE_CONF_PATH if a path with global.cylc is given.
    """

    globalfile = (tmp_path / GLOBALFILE)
    globalfile.parent.mkdir(parents=True, exist_ok=True)
    globalfile.touch()
    result = _pick_config_file(str(tmp_path))
    assert result[0] == 'cylc config --json'.split()
    assert 'CYLC_SITE_CONF_PATH' in result[1]
    assert result[1]['CYLC_SITE_CONF_PATH'] == str(tmp_path)


def test_pick_config_file_bad(tmp_path):
    """It raises an error if a bad path is given."""
    with pytest.raises(FileNotFoundError, match='No Cylc config file'):
        _pick_config_file(str(tmp_path))


def test_handle_cylc_config_returncode_compat():
    """It handles failure caused by a pre --json version of cylc config"""
    sub = SimpleNamespace()
    sub.stderr = b'no such option: --json'
    with pytest.raises(DependencyError, match='this version of Cylc'):
        _handle_cylc_config_returncode(sub)


def test_handle_cylc_config_other_errors():
    """It handles other failures"""
    sub = SimpleNamespace()
    sub.stderr = b'Hugs and Bunnies Error'
    with pytest.raises(Exception, match='Hugs'):
        _handle_cylc_config_returncode(sub)


def test_load_cfg_bad(tmp_path):
    """Overall test of load_cfg (closer to an integration test really)"""
    (tmp_path / 'flow.cylc').write_text("[scheduler]")
    with pytest.raises(Exception, match=r'missing \[scheduling\]'):
        load_cfg(tmp_path)


def test_load_cfg_good(tmp_path):
    """Overall test of load_cfg (closer to an integration test really)"""
    (tmp_path / 'flow.cylc').write_text("""
        [scheduler]
        [scheduling]
            [[graph]]
                R1 = foo
        [runtime]
            [[foo]]
    """)
    load_cfg(tmp_path)


def test_custom_items_recursive():
    """It recursively indents sections"""
    data = {'foo': {'bar': {'baz': 'qux'}}}
    ret = custom_items(data)
    assert ret == [':foo:\n   :bar:\n      :baz:\n         qux']


def test_custom_items_include():
    """It will include specified items."""
    data = {
        'a': '42',
        'b': '44',
    }
    assert custom_items(data, these=['a']) == [':a:\n   42']


@pytest.mark.parametrize(
    'input_, expect',
    (
        param(
            {'meta': {'foo': 'Hello World'}},
            ['.. cylc:conf:: foo', '   :foo:', '      Hello World'],
            id='abitrary-definitions'
        ),
        param(
            {'meta': {'title': 'My Workflow'}},
            ['.. cylc:conf:: My Workflow'],
            id='title-given'
        ),
        param(
            {'meta': {'URL': 'https://myworkflow.institution.ac.uk'}},
            [
                '.. cylc:conf:: foo',
                '   .. seealso:: https://myworkflow.institution.ac.uk',
            ],
            id='url'
        ),
        param(
            {'meta': {'description': 'Hello World\nIt\'s a multi-line str'}},
            [
                '.. cylc:conf:: foo',
                '   Hello World',
                "   It's a multi-line str"
            ],
            id='title-inferred'
        ),
        param(
            {
                'runtime': {
                    'task1': {
                        'platform': 'Skaerloey',
                        'environment': {
                            'ICECREAM': 'Neapolitan',
                            'SPRINKLES': "false",
                        },
                        'meta': {
                            'title': 'This task has a title',
                            'URL': 'https://foo.bar.baz/qux',
                            'description': 'Multi-\n-line\nDescription.',
                            'kustom': 'Custom metadata',
                        }
                    },
                    'task2': {
                        # title defaults to task name
                    }
                }
            },
            [
                '.. cylc:conf:: foo',
                '   .. cylc:conf:: This task has a title (task1)',
                '      :URL: https://foo.bar.baz/qux',
                '      Multi-',
                '      -line',
                '      Description.',
                '      :kustom:',
                '         Custom metadata',
                '      :platform:',
                '         Skaerloey',
                '      :environment:',
                '         :ICECREAM:',
                '            Neapolitan',
                '         :SPRINKLES:',
                '            false',
                '   .. cylc:conf:: task2',
                '      No metadata for this task.',
            ],
            id='task-basic'
        ),
    )
)
def test_workflow_config_to_node(input_, expect):
    """Workflow config object can convert workflow config to sphinx format.

    (More in the nature of an integration test)"""
    ret = [
        i for i in
        CylcWorkflowDirective.config_to_node(
            input_,
            src='foo',
            task_items=['platform', 'environment']
        )
        if i   # Filter blank lines
    ]
    assert ret == expect


@pytest.fixture(scope='module')
def setup_global_cfg():
    cfg = {
        'platforms': {
            # Check that sensible defaults are inserted:
            'default': {},
            'foo': {
                'hosts': ['foo1', 'foo2', 'foo3'],
                'job runner': 'raspbs'
            },
            'regex.*with.*title': {
                'hosts': ['a1', 'a2'],
                'meta': {
                    'title': 'Has a title set by meta',
                    'URL': 'https://foo.bar',
                    'description': 'More\nthan\n1\nline',
                    'custom entry': 'Yes, really',
                    'custom subsection': {
                        'Rugs': 'and sunny',
                        'ever': {'deeper': {'subsections': 'if you must'}}
                    }
                }
            },
        },
        'platform groups': {
            'groupB': {
                'platforms': ['foo']
            },
            'groupA': {
                'platforms': ['foo', 'default']
            }
        }
    }
    return [
        i for i in
        CylcGlobalDirective.config_to_node(
            cfg,
            src='bar',
        )
        if i   # Filter blank lines
    ]


def test_platforms_order(setup_global_cfg):
    """Definition order is reversed to demonstrate Cylc behaviour."""
    assert [
        p for p in setup_global_cfg
        if p.strip().startswith('.. cylc:conf::')
    ] == [
        '.. cylc:conf:: bar',
        '   .. cylc:conf:: platform groups',
        '      .. cylc:conf:: groupA',
        '      .. cylc:conf:: groupB',
        '   .. cylc:conf:: platforms',
        '      .. cylc:conf:: Has a title set by meta',
        '      .. cylc:conf:: foo',
        '      .. cylc:conf:: default',
    ]


def test_platforms_title_fm_meta(setup_global_cfg):
    """If title set in meta that is preferred and a regex is added"""
    assert '      .. cylc:conf:: Has a title set by meta' in setup_global_cfg
    assert '         :regex: ``regex.*with.*title``' in setup_global_cfg


def test_platforms_job_runners(setup_global_cfg):
    """Job runner always inserted."""
    assert [p for p in setup_global_cfg if ":job runner:" in p] == [
        "         :job runner: background",
        "         :job runner: background",
        "         :job runner: background",
        "         :job runner: raspbs",
        "         :job runner: background",
    ]


def test_platforms_selectable_lister(setup_global_cfg):
    """It lists hosts or plaftforms nicely."""
    assert [p for p in setup_global_cfg if ":hosts:" in p] == [
        '         :hosts: ``a1``, ``a2``',
        '         :hosts: ``foo1``, ``foo2``, ``foo3``',
        '         :hosts: ``default``',
    ]
    assert [p for p in setup_global_cfg if ":platforms:" in p] == [
        '         :platforms: ``foo``, ``default``',
        '         :platforms: ``foo``',
    ]


def test_platforms_multiline_descriptions(setup_global_cfg):
    """Check multiline descriptions are handled and block indented."""
    assert 'More\n         than\n         1\n         line' in '\n'.join(
        setup_global_cfg)


def test_platforms_selectable_user_metadata(setup_global_cfg):
    """Mop up deep metadata handling"""
    for item in [
        '         :URL: https://foo.bar',
        '         :custom entry:',
        '            Yes, really',
        '         :custom subsection:',
        '            :Rugs:',
        '               and sunny',
        '            :ever:',
        '               :deeper:',
        '                  :subsections:',
        '                     if you must',
    ]:
        assert item in setup_global_cfg
