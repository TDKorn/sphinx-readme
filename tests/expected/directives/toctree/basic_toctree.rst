.. |A subheading with a cross-reference to  TestClass| replace:: A subheading with a cross-reference to  ``TestClass``
.. _A subheading with a cross-reference to  TestClass: https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-subheading-with-a-cross-reference-to-testclass
.. |Another section heading, with  inline markup| replace:: Another section heading, with  ``inline markup``
.. _Another section heading, with  inline markup: https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#another-section-heading-with-inline-markup
.. |File containing a toctree, to test parsing of sub-toctrees| replace:: File containing a ``toctree``, to test parsing of sub-toctrees
.. _File containing a toctree, to test parsing of sub-toctrees: https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/sub_toctree.html
.. |sphinx_readme test package| replace:: ``sphinx_readme`` test package
.. _sphinx_readme test package: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html
.. |test_function()| replace:: ``test_function()``
.. _test_function(): https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.test_function
.. |TEST_VARIABLE| replace:: ``TEST_VARIABLE``
.. _TEST_VARIABLE: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TEST_VARIABLE
.. |TestClass| replace:: ``TestClass``
.. _TestClass: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TestClass
.. |TestClass.test_attr| replace:: ``TestClass.test_attr``
.. _TestClass.test_attr: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TestClass.test_attr
.. |TestClass.test_cached_property| replace:: ``TestClass.test_cached_property``
.. _TestClass.test_cached_property: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TestClass.test_cached_property
.. |TestClass.test_method()| replace:: ``TestClass.test_method()``
.. _TestClass.test_method(): https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TestClass.test_method
.. |TestClass.test_property| replace:: ``TestClass.test_property``
.. _TestClass.test_property: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TestClass.test_property
.. |TestException| replace:: ``TestException``
.. _TestException: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#test_package.test_module.TestException
.. |The  test_module  module| replace:: The  ``test_module``  module
.. _The  test_module  module: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#module-test_package.test_module


Basic Toctree
-----------------

This file contains a toctree with entries from files in parent directories and subdirectories

It contains entries that have explicit titles, subtoctrees, and subtoctrees with self entries

**Toctree Caption**

* |sphinx_readme test package|_

  * |The  test_module  module|_

    * |TEST_VARIABLE|_
    * |TestClass|_

      * |TestClass.test_attr|_
      * |TestClass.test_cached_property|_
      * |TestClass.test_method()|_
      * |TestClass.test_property|_

    * |TestException|_
    * |test_function()|_


* |File containing a toctree, to test parsing of sub-toctrees|_

  * `A random section heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/sub_toctree.html#a-random-section-heading>`_

    * `File in the subfolder <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html>`_

      * `A section heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-section-heading>`_

        * `A subheading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-subheading>`_
        * |A subheading with a cross-reference to  TestClass|_

      * |Another section heading, with  inline markup|_



* `Entry with explicit title <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html>`_

  * `A section heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-section-heading>`_

    * `A subheading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-subheading>`_
    * |A subheading with a cross-reference to  TestClass|_

  * |Another section heading, with  inline markup|_

* `Self Toctree <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/self_toctree.html>`_

  * `This is a heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/self_toctree.html#this-is-a-heading>`_

    * `Self Toctree <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/self_toctree.html>`_



      |

