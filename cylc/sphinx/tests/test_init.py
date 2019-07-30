from unittest.mock import Mock

from cylc.sphinx import register_static


def test_register_static():
    app = Mock()
    app.config = Mock()
    app.config.html_static_path = []

    register_static(app, 'cylc.sphinx.foo')
    assert app.config.html_static_path[0].endswith(
        'cylc/sphinx/foo/_static'
    )

    register_static(app, 'cylc.sphinx.foo.bar')
    assert app.config.html_static_path[1].endswith(
        'cylc/sphinx/foo/bar/_static'
    )
