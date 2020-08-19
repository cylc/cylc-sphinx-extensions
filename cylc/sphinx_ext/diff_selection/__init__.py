"""Makes text selection in diff code-blocks fool-proof.

Designed to assist with tutorial material for ``diff`` code-blocks:

* Makes ``-`` lines non-selectable.
* Makes ``+`` symbol non-selectable.

.. note::

   Extension is automatically loaded when added to extensions, no directives or
   configurations required.


.. rubric:: Example

.. code-block:: rst

   .. code-block:: diff

        foo
      + bar
      - baz
        pub

.. code-block:: diff

    foo
  + bar
  - baz
    pub

"""


from cylc.sphinx_ext import register_static


__version__ = '1.0.0'

__all__ = ['setup']


def setup(app):
    """Sphinx plugin setup function."""
    register_static(app, __name__)
    return {'version': __version__, 'parallel_read_safe': True}
