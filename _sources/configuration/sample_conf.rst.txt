Sample ``conf.py``
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   extensions = [
      "sphinx_readme",
   ]

   html_context = {
      'display_github': True,
      'github_user': 'TDKorn',
      'github_repo': 'sphinx-readme',
   }

   html_baseurl = "https://sphinx-readme.readthedocs.io/en/latest"

   readme_src_files = "README.rst"

   readme_docs_url_type = "code"



.. important:: For platforms that don't support the ``raw`` directive (PyPi, GitLab, and BitBucket),
   be sure to disable :confval:`readme_raw_directive`:

   .. code-block:: python

      readme_raw_directive = False
