"""Patches the Read The Docs Sphinx Theme.

.. _Read The Docs Theme: https://github.com/readthedocs/sphinx_rtd_theme

.. warning::

   These modifications only work in the `Read The Docs Theme`_

.. note::

   extension is automatically loaded when added to extensions, no directives or
   configurations required.


Modifications:

1. Permit nested admonitions of differing class

   .. note::

      .. error::

         The inner admonition should appear in a different colour to the outer
         one.

2. Permit linking admonitions

   .. note::

      When hovering the title of this admonition a link symbol should appear.

3. Add warning symbols before deprecated items.

   .. deprecated:: 1.2.3

      Oh no!

4. Make versionchanged items more prominent.

   .. versionchanged:: 1.2.3

      Something changed!

5. Restyle code-block captions

6. Address lack of whitespace under lists in admonitions

7. Improve sidebar scrolling

Extension is automatically loaded for all code diffs when it is added to
a project's Sphinx extensions. No directives required.

"""

from cylc.sphinx_ext import register_static


__version__ = '1.0.0'

__all__ = ['setup']


def setup(app):
    """Sphinx plugin setup function."""
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
