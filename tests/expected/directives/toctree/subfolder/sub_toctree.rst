.. |A subheading with a cross-reference to  TestClass| replace:: A subheading with a cross-reference to  ``TestClass``
.. _A subheading with a cross-reference to  TestClass: https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-subheading-with-a-cross-reference-to-testclass
.. |Another section heading, with  inline markup| replace:: Another section heading, with  ``inline markup``
.. _Another section heading, with  inline markup: https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#another-section-heading-with-inline-markup


File containing a ``toctree``, to test parsing of sub-toctrees
--------------------------------------------------------------------

This file contains a basic toctree.

When a toctree contains this file as an entry, it allows for testing the parsing of sub-toctrees.


A random section heading
===========================

Here is the toctree


**Toctree Caption**

* `File in the subfolder <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html>`_

  * `A section heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-section-heading>`_

    * `A subheading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-subheading>`_
    * |A subheading with a cross-reference to  TestClass|_

  * |Another section heading, with  inline markup|_


    |

