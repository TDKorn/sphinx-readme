.. |sphinx+only| replace:: ``only``
.. _sphinx+only: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-only
.. |sphinx+rubric| replace:: ``rubric``
.. _sphinx+rubric: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-rubric
.. |sphinx+usage/domains/restructuredtext+reStructuredText Domain| replace:: reStructuredText Domain
.. _sphinx+usage/domains/restructuredtext+reStructuredText Domain: https://www.sphinx-doc.org/en/master/usage/domains/restructuredtext.html
.. |sphinx+usage/domains/standard+Standard Domain| replace:: Standard Domain
.. _sphinx+usage/domains/standard+Standard Domain: https://www.sphinx-doc.org/en/master/usage/domains/standard.html
.. |.~.sphinx.domains.python.PythonDomain| replace:: ``PythonDomain``
.. _.~.sphinx.domains.python.PythonDomain: https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.python.PythonDomain
.. |.~.sphinx.environment.BuildEnvironment| replace:: ``BuildEnvironment``
.. _.~.sphinx.environment.BuildEnvironment: https://www.sphinx-doc.org/en/master/extdev/envapi.html#sphinx.environment.BuildEnvironment
.. |.~.test_function| replace:: ``test_function()``
.. _.~.test_function: https://github.com/TDKorn/sphinx-readme/blob/main/tests/test_package/test_module.py#L11-L12
.. |.~.TestClass| replace:: ``TestClass``
.. _.~.TestClass: https://github.com/TDKorn/sphinx-readme/blob/main/tests/test_package/test_module.py#L1-L8


.. |env| replace:: |.~.sphinx.environment.BuildEnvironment|_
.. |std_domain| replace:: |sphinx+usage/domains/standard+Standard Domain|_
.. |rubric| replace:: |sphinx+rubric|_
.. |test_class| replace:: |.~.TestClass|_


File-Level Substitution Definitions
========================================

The substitution definitions for external cross-references to the |env|, |std_domain|, and |rubric| are
defined at the top of the file.

There's also a substitution definition for a non-intersphinx cross-reference to the |test_class|


Substitution Definitions in Only Directives
=============================================

.. |py_domain| replace:: |.~.sphinx.domains.python.PythonDomain|_
.. |rst_domain| replace:: |sphinx+usage/domains/restructuredtext+reStructuredText Domain|_
.. |only| replace:: |sphinx+only|_
.. |test_function| replace:: |.~.test_function|_


The substitution definitions for external cross-references to the |py_domain|, |rst_domain|, and |only| directive
are defined within this |only| directive

There's also a substitution definition for a non-intersphinx cross-reference to the |test_function|

