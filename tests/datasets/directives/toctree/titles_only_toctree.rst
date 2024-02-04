Titles Only Toctree
--------------------

This file contains a toctree with entries from files in parent directories and subdirectories

It contains entries that have explicit titles, subtoctrees, and subtoctrees with self entries

The toctree uses the ``:titlesonly:`` flag

* Note that this flag doesn't apply when this toctree is a sub-toctree, like in :doc:`/index`


.. toctree::
   :caption: Toctree Caption
   :titlesonly:

   ../../modules
   Entry with explicit title <subfolder/contents>
   subfolder/self_toctree