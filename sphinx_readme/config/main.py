import os
import re
import copy
from pathlib import Path
from collections import defaultdict
from typing import Union, List, Dict
from functools import cached_property

from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

from sphinx_readme.utils import get_conf_val, set_conf_val, logger
from sphinx_readme.config import get_repo_url, get_linkcode_url, get_linkcode_resolve


class READMEConfig:

    REFERENCE_MAPPING = {
        "replace": None,
        "target": None,
    }

    def __init__(self, app: Sphinx):
        self.logger = logger
        self.src_dir = app.srcdir
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

        self.repo_url = self.get_repo_url(app)
        self.docs_url = self.get_docs_url(app)
        self.ref_map = self.get_ref_map()
        self.source_files = self.read_source_files()

        if self.docs_url_type == "code":
            self.setup_linkcode_resolve(app)

    def get_repo_url(self, app: Sphinx):
        if repo_url := get_conf_val(app, "readme_repo_url"):
            return repo_url.rstrip("/")

        if self.html_context:
            return get_repo_url(self.html_context)

        raise ExtensionError(
            "sphinx_readme: conf.py value must be set for "
            "``readme_repo_url`` or ``html_context``"
        )

    def get_docs_url(self, app: Sphinx) -> str:
        if docs_url := get_conf_val(app, "readme_docs_url") is None:
            # Generate docs URL from other conf.py values
            if self.docs_url_type == "html":
                if self.html_baseurl:
                    docs_url = self.html_baseurl
                else:
                    raise ExtensionError(
                        "sphinx_readme: conf.py value must be set for "
                        "``readme_docs_url`` or ``html_baseurl``"
                    )
            else:  # ``docs_url_type`` is "code"
                docs_url = self.repo_url

        return docs_url.rstrip("/")

    def setup_linkcode_resolve(self, app: Sphinx) -> None:
        linkcode_func = get_conf_val(app, "linkcode_resolve")

        if not callable(linkcode_func):
            self.logger.info(
                "``sphinx_readme:`` Function `linkcode_resolve` not found in ``conf.py``; "
                "using default function from ``sphinx_readme``"
            )
            # Get the template for linking to source code
            linkcode_url = get_linkcode_url(
                url=self.repo_url,
                context=self.html_context,
                blob=get_conf_val(app, 'linkcode_blob')
            )
            linkcode_func = get_linkcode_resolve(linkcode_url)

        set_conf_val(app, 'linkcode_resolve', linkcode_func)
        app.setup_extension("sphinx.ext.linkcode")

    def get_ref_map(self) -> Dict:
        refs = defaultdict(_map_entry)
        refs['ref'] = []
        refs['doc'] = []
        return refs

    def read_source_files(self) -> Dict[str, str]:
        sources = {
            src_file: self.read_rst(src_file)
            for src_file in self.src_files
        }
        return sources

    def read_rst(self, rst_file: Union[str, Path]):
        with open(rst_file, 'r', encoding='utf-8') as f:
            rst = f.read()

        include_pattern = r"^\.\. include:: ([./]*?[\w/-]+\.rst)"

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
                    file = Path(f"{self.src_dir}/{include}").resolve()

                else:
                    # These paths are relative to rst_file dir
                    file = (Path(rst_file).parent / Path(include)).resolve()

                # Sub in the file content
                rst = re.sub(
                    pattern=rf".. include:: {include}",
                    repl=self.read_rst(file).replace(r'\n', r'\\n'),
                    string=rst
                )
        else:
            # Remove all include directives from the text
            rst = re.sub(include_pattern, '', rst, flags=re.M)

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
    def out_dir(self, out_dir: str):
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        self._out_dir = Path(out_dir).resolve()

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
    def icon_map(self):
        types = ("attention", "caution", "danger", "error", "hint", "important", "note", "tip", "warning", "default")
        icons = ("⚠", "⚠", "☢", "❌", "🧠", "‼", "📝", "💡", "❗", self.default_admonition_icon)
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


def _map_entry():
    return copy.deepcopy(READMEConfig.REFERENCE_MAPPING)
