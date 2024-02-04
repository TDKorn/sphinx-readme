.. |Another section heading, with  inline markup| replace:: Another section heading, with  ``inline markup``
.. _Another section heading, with  inline markup: https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#another-section-heading-with-inline-markup
.. |.index| replace:: Table of Contents
.. _.index: https://sphinx-readme-testing.readthedocs.io/en/latest/index.html
.. |sphinx_readme test package| replace:: ``sphinx_readme`` test package
.. _sphinx_readme test package: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html
.. |The  test_module  module| replace:: The  ``test_module``  module
.. _The  test_module  module: https://sphinx-readme-testing.readthedocs.io/en/latest/modules.html#module-test_package.test_module


Max Depth Toctree
---------------------

This file contains a toctree with entries from files in parent directories and subdirectories

It contains entries that have explicit titles, subtoctrees, and subtoctrees with self entries

The toctree has a ``maxdepth`` of 2

* Note that this flag doesn't apply when this toctree is a sub-toctree, like in |.index|_

**Toctree Caption**

* |sphinx_readme test package|_

  * |The  test_module  module|_



* `Entry with explicit title <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html>`_

  * `A section heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/contents.html#a-section-heading>`_


  * |Another section heading, with  inline markup|_

* `Self Toctree <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/self_toctree.html>`_

  * `This is a heading <https://sphinx-readme-testing.readthedocs.io/en/latest/directives/toctree/subfolder/self_toctree.html#this-is-a-heading>`_




    |

