"""A borderless table for simple grid layouts.

Re-styles the Sphinx built-in :rst:dir:`list-table` directive.

Extension is automatically loaded for all code diffs when it is added to
a project's Sphinx extensions. No directives required.

.. rubric:: Example

.. code-block:: rst

   .. list-table::
      :class: grid-table

      * - ..rubric:: Col1 Header
        - ..rubric:: Col2 Header
      * -
          .. code-block:: none

             Col 1 Row 1
      * -
          .. code-block:: none

             Col 2 Row 1

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
    app.add_css_file('css/grid_table.css')
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
