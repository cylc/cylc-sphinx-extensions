"""A borderless table for simple grid layouts.

Re-styles the Sphinx built-in ``list-table`` directive.

.. note::

   Extension is automatically loaded when added to extensions, no directives or
   configurations required.


.. rst-example::

   .. list-table::
      :class: grid-table

      * - .. rubric:: Col1 Header
        - .. rubric:: Col2 Header
      * -
          .. code-block:: none

             Col 1 Row 1
        -
          .. code-block:: none

             Col 2 Row 1

"""

from cylc.sphinx_ext import register_static


__version__ = '1.0.0'

__all__ = ['setup']


def setup(app):
    """Sphinx plugin setup function."""
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
