{#
   template for minimal documentation of a module (i.e. docstring only)
#}

{{ fullname.split(".")[-1] | escape | underline}}

.. automodule:: {{ fullname }}
