from unittest.mock import Mock

from cylc.sphinx_ext import register_static


def test_register_static():
    app = Mock()
    app.config = Mock()
    app.config.html_static_path = []

    register_static(app, 'cylc.sphinx_ext.foo')
    assert app.config.html_static_path[0].endswith(
        'cylc/sphinx_ext/foo/_static'
    )

    register_static(app, 'cylc.sphinx_ext.foo.bar')
    assert app.config.html_static_path[1].endswith(
        'cylc/sphinx_ext/foo/bar/_static'
    )
