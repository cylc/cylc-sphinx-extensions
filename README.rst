Cylc Sphinx Extensions
======================

A library of extensions for documenting Cylc projects.

Installation
------------

.. code-block:: console

   $ pip install git+https://github.com/cylc/cylc-sphinx-extensions.git

Usage
-----

Register extensions in your project's ``conf.py``:

.. code-block:: python

   extension = [
       'cylc.sphinx.cylc_lang'
   ]

Development
-----------

Fork and clone ``https://github.com/cylc/cylc-sphinx-extensions.git``.

Build documentation by running:

.. code-block:: sub

   $ make clean <format>  # e.g. make html

This documentation build serves as a simple test battery, warnings will cause
it to fail.

Unittests and Doctests are run by pycodestyle:

.. code-block:: console

   $ pycodestyle .

Extensions are auto-documented from their module docstrings.
