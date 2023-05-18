import copy
from pathlib import Path
from collections import defaultdict
from typing import Union, List, Dict

from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from sphinx_readme.utils import get_conf_val, set_conf_val, read_rst, logger
from sphinx_readme.config import get_linkcode_url, get_linkcode_resolve



class READMEConfig:

    REFERENCE_MAPPING = {
        "module": None,
        "fullname": None,
        "replace": None,
        "target": None
    }

    def __init__(self, app: Sphinx):
        self.logger = logger
        self.src_dir = app.srcdir

        self.out_dir = get_conf_val(app, 'readme_out_dir')
        self.src_files = get_conf_val(app, 'readme_src_files', [])
        self.replace_attrs = get_conf_val(app, 'readme_replace_attrs')
        self.inline_markup = get_conf_val(app, 'readme_inline_markup')
        self.raw_directive = get_conf_val(app, 'readme_raw_directive')
        self.include_directive = get_conf_val(app, 'readme_include_directive')

        self.docs_url = self.get_docs_url(app)
        self.linkcode_url = get_linkcode_url(
            blob=get_conf_val(app, 'linkcode_blob'),
            url=get_conf_val(app, 'linkcode_url'),
            context=get_conf_val(app, 'html_context')
        )
        self.setup_linkcode_resolve(app)

        self.readme_sources = self.read_source_files()
        self.ref_map = self.get_ref_map()

    def get_docs_url(self, app: Sphinx) -> str:
        docs_url = get_conf_val(app, "readme_docs_url", get_conf_val(app, "html_baseurl", "")).rstrip("/")
        if not docs_url:
            raise ExtensionError(
                "sphinx_readme: conf.py value must be set for ``readme_docs_url`` or ``html_baseurl``"
            )
        return docs_url

    def get_ref_map(self) -> Dict:
        refs = defaultdict(_map_entry)
        refs['ref'] = []
        refs['doc'] = []
        return refs

    def setup_linkcode_resolve(self, app: Sphinx) -> None:
        linkcode_func = get_conf_val(app, "linkcode_resolve")

        if not callable(linkcode_func):
            self.logger.info(
                "``sphinx_readme:`` Function `linkcode_resolve` not found in ``conf.py``; "
                "using default function from ``sphinx_readme``"
            )
            linkcode_func = get_linkcode_resolve(self.linkcode_url)

        set_conf_val(app, 'linkcode_resolve', linkcode_func)

    def read_source_files(self) -> Dict[str, str]:
        # Create dict of {file: text} - all parsing is done on this text
        sources = {
            src_file: read_rst(str(src_file), parse_include=self.include_directive)
            for src_file in self.src_files
        }
        return sources

    @property
    def src_files(self):
        return self._src_files

    @src_files.setter
    def src_files(self, src_files: Union[str, List[str]]):
        if isinstance(src_files, str):
            src_files = [src_files]

        self._src_files = [  # Absolute path of files; files should be relative to source directory
            str((Path(self.src_dir) / Path(src_file)).resolve())
            for src_file in src_files
        ]

    @property
    def docs_url_type(self):
        return 'code' if self.docs_url in self.linkcode_url else 'html'


def _map_entry():
    return copy.deepcopy(READMEConfig.REFERENCE_MAPPING)
