.. |.~.test_function| replace:: ``test_function()``
.. _.~.test_function: https://github.com/TDKorn/sphinx-readme/blob/main/tests/test_package/test_module.py#L31-L32
.. |.~.TestClass| replace:: ``TestClass``
.. _.~.TestClass: https://github.com/TDKorn/sphinx-readme/blob/main/tests/test_package/test_module.py#L7-L23


.. |env| replace:: ``BuildEnvironment``
.. |std_domain| replace:: ``Standard Domain``
.. |rubric| replace:: ``rubric``
.. |test_class| replace:: |.~.TestClass|_


File-Level Substitution Definitions
========================================

The substitution definitions for external cross-references to the |env|, |std_domain|, and |rubric| are
defined at the top of the file.

There's also a substitution definition for a non-intersphinx cross-reference to the |test_class|


Substitution Definitions in Only Directives
=============================================

.. |py_domain| replace:: ``PythonDomain``
.. |rst_domain| replace:: ``reStructuredText Domain``
.. |only| replace:: ``only``
.. |test_function| replace:: |.~.test_function|_


The substitution definitions for external cross-references to the |py_domain|, |rst_domain|, and |only| directive
are defined within this |only| directive

There's also a substitution definition for a non-intersphinx cross-reference to the |test_function|

