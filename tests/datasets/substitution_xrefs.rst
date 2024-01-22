.. |env| replace:: :class:`~.sphinx.environment.BuildEnvironment`
.. |std_domain| replace:: :external+sphinx:doc:`Standard Domain <usage/domains/standard>`
.. |rubric| replace:: :rst:dir:`rubric`
.. |test_class| replace:: :class:`~.TestClass`


File-Level Substitution Definitions
========================================

The substitution definitions for external cross-references to the |env|, |std_domain|, and |rubric| are
defined at the top of the file.

There's also a substitution definition for a non-intersphinx cross-reference to the |test_class|


.. only:: readme

   Substitution Definitions in Only Directives
   =============================================

   .. |py_domain| replace:: :class:`~.sphinx.domains.python.PythonDomain`
   .. |rst_domain| replace:: :doc:`reStructuredText Domain <sphinx:usage/domains/restructuredtext>`
   .. |only| replace:: :rst:dir:`only`
   .. |test_function| replace:: :func:`~.test_function`


   The substitution definitions for external cross-references to the |py_domain|, |rst_domain|, and |only| directive
   are defined within this |only| directive

   There's also a substitution definition for a non-intersphinx cross-reference to the |test_function|
