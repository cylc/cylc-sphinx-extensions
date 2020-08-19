"""Patches the hard-coded Heroglyph slides theme.

.. _Heroglyph: https://github.com/nyergler/hieroglyph

.. warning::

   These modifications only in `Heroglyph`_ slides builds.

.. nextslide::

.. note::

   extension is automatically loaded when added to extensions, no directives or
   configurations required.

.. nextslide::

1. Make quotations small enough to fit on the slide.

   A quotation should not overwhelm the entire slide, it should fit in neatly

   -- Me

.. nextslide::

2. Add a bit of space between slide titles and images.

.. nextslide::

3. Don't display glossary terms as hyperlinks.

.. nextslide::

4. Make code-block captions legible.

   .. code-block:: bash
      :caption: Hello World

      $ echo 'hello world'

"""


from cylc.sphinx_ext import register_static


__version__ = '1.0.0'

__all__ = ['setup']


def setup(app):
    """Sphinx plugin setup function."""
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
