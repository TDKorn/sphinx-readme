import re
from pathlib import Path
from typing import Union, List, Dict
from functools import cached_property

from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

from sphinx_readme.utils import get_conf_val, set_conf_val, logger, replace_only_directives, remove_raw_directives
from sphinx_readme.config import get_repo_dir, get_repo_host, get_blob_url, get_repo_url, get_linkcode_url, get_linkcode_resolve


class READMEConfig:

    def __init__(self, app: Sphinx):
        self.logger = logger
        self.src_dir = Path(app.srcdir)
        self.repo_dir = get_repo_dir()
        self.out_dir = get_conf_val(app, 'readme_out_dir')
        self.src_files = get_conf_val(app, 'readme_src_files', [])
        self.html_context = get_conf_val(app, "html_context")
        self.html_baseurl = get_conf_val(app, "html_baseurl", "").rstrip("/")
        self.docs_url_type = get_conf_val(app, 'readme_docs_url_type')
        self.replace_attrs = get_conf_val(app, 'readme_replace_attrs')
        self.inline_markup = get_conf_val(app, 'readme_inline_markup')
        self.raw_directive = get_conf_val(app, 'readme_raw_directive')
        self.rubric_heading = get_conf_val(app, 'readme_rubric_heading')
        self.admonition_icons = get_conf_val(app, 'readme_admonition_icons')
        self.include_directive = get_conf_val(app, 'readme_include_directive')
        self.default_admonition_icon = get_conf_val(app, 'readme_default_admonition_icon')

        self.repo_blob = get_conf_val(app, "readme_blob")
        self.repo_url = self.get_repo_url()
        self.blob_url = get_blob_url(
            repo_url=self.repo_url,
            blob=self.repo_blob
        )
        self.docs_url = self.get_docs_url()
        self.source_files = self.read_source_files()

        if self.docs_url_type == "code":
            self.setup_linkcode_resolve(app)

    def get_repo_url(self) -> str:
        """Generates the repository URL from the :external+sphinx:confval:`html_context` dict

        :raises ExtensionError: if ``html_context`` is not set or missing values
        """
        if not self.html_context:
            raise ExtensionError(
                "``sphinx_readme``: conf.py value "
                "must be set for ``html_context``"
            )
        return get_repo_url(self.html_context)

    def get_docs_url(self) -> str:
        """Returns the base URL of the documentation source to use
        when resolving :mod:`~.sphinx.ext.autodoc` cross-references

         If :attr:`docs_url_type` is

         * ``"code"``: uses the :attr:`blob_url`
         * ``"html"``: uses the :confval:`html_baseurl`

        :raises ExtensionError: if ``html_baseurl`` is missing
        """
        if self.docs_url_type == "html":
            if self.html_baseurl:
                docs_url = self.html_baseurl
            else:
                raise ExtensionError(
                    "``sphinx_readme``: conf.py value "
                    "must be set for ``html_baseurl``"
                )
        else:  # ``docs_url_type`` is "code"
            docs_url = self.blob_url

        return docs_url.rstrip("/")

    def setup_linkcode_resolve(self, app: Sphinx) -> None:
        linkcode_func = get_conf_val(app, "linkcode_resolve")

        if not callable(linkcode_func):
            self.logger.info(
                "``sphinx_readme:`` using default ``linkcode_resolve``"
            )
            # Get the template for linking to source code
            linkcode_url = get_linkcode_url(self.blob_url)
            linkcode_func = get_linkcode_resolve(linkcode_url)

        set_conf_val(app, 'linkcode_resolve', linkcode_func)
        app.setup_extension("sphinx.ext.linkcode")


    def read_source_files(self) -> Dict[str, str]:
        sources = {
            src_file: self.read_rst(src_file)
            for src_file in self.src_files
        }
        return sources

    def read_rst(self, rst_file: Union[str, Path], replace_only: bool = False) -> str:
        with open(rst_file, 'r', encoding='utf-8') as f:
            rst = f.read()

        if replace_only:
            rst = replace_only_directives(rst)

        include_pattern = r"\.\. include:: ([./]*?[\w/-]+\.\w+?)$"

        if self.include_directive:
            # Find all included files
            included = re.findall(
                pattern=include_pattern,
                string=rst,
                flags=re.M
            )
            for include in included:
                # Determine abs path of included file
                if include.startswith("/"):
                    # These paths are relative to source dir
                    file = Path(f"{self.src_dir}{include}").resolve()
                else:
                    # These paths are relative to rst_file dir
                    file = (Path(rst_file).parent / Path(include)).resolve()

                if file.exists():
                    # Replace directive with the file content
                    repl = self.read_rst(file, replace_only).replace(r'\n', r'\\n')
                else:
                    # Remove the directive
                    repl = ''
                    self.logger.error(
                        f"``sphinx_readme``: included file {file} does not exist"
                    )
                rst = re.sub(
                    pattern=rf".. include:: {include}",
                    repl=repl,
                    string=rst
                )
        else:
            # Remove all include directives from the text
            rst = re.sub(include_pattern, '', rst, flags=re.M)

        if self.raw_directive is False:
            rst = remove_raw_directives(rst)

        return rst

    @property
    def src_files(self):
        return self._src_files

    @src_files.setter
    def src_files(self, src_files: Union[str, List[str]]):
        if isinstance(src_files, str):
            src_files = [src_files]

        self._src_files = [  # Absolute paths of files; files should be relative to source directory
            str((Path(self.src_dir) / Path(src_file)).resolve())
            for src_file in src_files
        ]

    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, out: str):
        out_dir = Path(out)

        if not out_dir.is_absolute():
            out_dir = (self.src_dir / out_dir).resolve()

        if not out_dir.exists():
            out_dir.mkdir()

        self._out_dir = out_dir

    @property
    def docs_url_type(self):
        return self._docs_url_type

    @docs_url_type.setter
    def docs_url_type(self, docs_url_type: str):
        if docs_url_type not in ('html', 'code'):
            raise ExtensionError(
                "``sphinx_readme``: ``readme_docs_url_type`` value must be ``code`` or ``html``"
            )
        if docs_url_type == "code" and not self.html_baseurl:
            raise ExtensionError(  # HTML url is needed for non-source code xrefs
                "``sphinx_readme``: conf.py value missing for ``html_baseurl``"
            )
        self._docs_url_type = docs_url_type

    @cached_property
    def repo_host(self):
        return get_repo_host(self.repo_url)

    @cached_property
    def image_baseurl(self):
        if self.repo_host == "github":
            # Ex. https://raw.githubusercontent.com/TDKorn/sphinx-readme/main
            return self.blob_url.replace("github.com", "raw.githubusercontent.com").replace('blob/', '')

        elif self.repo_host == "gitlab":
            # Ex. https://gitlab.com/TDKorn/sphinx-readme/raw/main
            return self.blob_url.replace("/blob/", "/raw/")

        else:
            # Ex. https://bitbucket.org/TDKorn/sphinx-readme/raw/main
            return self.blob_url.replace("/src/", "/raw/")


    @cached_property
    def icon_map(self):
        types = ("attention", "caution", "danger", "error", "hint", "important", "note", "tip", "warning", "default")
        icons = ("🔔️", "⚠️", "☢️", '⛔', "🧠", "📢", "📝", "💡", "🚩", self.default_admonition_icon)
        icon_map = dict(zip(types, icons))

        # Update/add custom admonition icons from conf.py
        if self.admonition_icons:
            if isinstance(self.admonition_icons, Dict):
                icon_map.update(self.admonition_icons)

        return icon_map

    @property
    def admonition_template(self):
        if self.raw_directive is True:
            return r'''
.. raw:: html

   <table>
       <tr align="left">
           <th>

{icon} {title}

.. raw:: html

   </th>
   <tr><td>

{text}

.. raw:: html

   </td></tr>
   </table>
'''
        else:
            return r'''
.. csv-table::
   :header: {icon} {title}

   "\1"
'''
