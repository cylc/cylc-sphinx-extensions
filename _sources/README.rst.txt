Cylc Sphinx Extensions
======================

A library of Sphinx extensions for documenting Cylc projects.


Installation
------------

Install all extensions (but not dependencies)::

   $ pip install cylc-sphinx-extensions

OR all extensions + dependencies for specified extension(s) by name::

   $ pip install cylc-sphinx-extensions.git[cylc_lang]

OR all extensions + dependencies for all extensions::

   $ pip install cylc-sphinx-extensions.git[all]

Note the ``minicylc`` extension requires ``graphviz``::

   # install graphviz from your package manager e.g:
   $ sudo apt-get install -y graphviz


Usage
-----

To use an extension register it in your project's ``conf.py`` e.g::

   extension = [
       'cylc.sphinx_ext.cylc_lang'
   ]

Some of these extensions are "auto-loading" and do not require any extra steps
to activate.

If the ``html_static_path`` configuration is set in your ``conf.py`` you will
need to move this into a ``setup`` function, otherwise extensions cannot append
to this path to add their own static resources e.g::

   def setup(app):
       app.config.html_static_path.append('_static')


Development
-----------

Fork and clone ``https://github.com/cylc/cylc-sphinx-extensions.git``.

Extensions are auto-documented from their module docstrings.

Build documentation by running::

   $ make clean <format>  # e.g. make html slides

This documentation build serves as a simple test battery (warnings will cause
it to fail), for everything else there's pytest::

   $ pytest

For code linting::

   $ pycodestyle .  # python
   $ eslint cylc/   # javascript
