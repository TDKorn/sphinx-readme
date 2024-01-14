import os
import sys
import inspect
from pathlib import Path
from functools import cached_property

from typing import Dict, Optional, Callable
from sphinx.errors import ExtensionError

from sphinx_readme.utils.git import get_repo_url, get_blob_url, get_repo_dir
from sphinx_readme.utils.sphinx import logger


def get_linkcode_url(
        blob_url: Optional[str] = None,
        repo_url: Optional[str] = None,
        context: Optional[Dict] = None,
        blob: Optional[str] = None
) -> str:
    """Generates the template URL for linking to highlighted source code

    Final links are generated from the template by a ``linkcode_resolve()`` function

    .. note:: Only one of ``blob_url``, ``repo_url``, or ``context`` needs to be specified

    :param blob_url: the base URL for a specific blob of a repository
    :param repo_url: the base URL of a repository
    :param context: the Sphinx :external+sphinx:confval:`html_context` dict
    :param blob: the blob of the repository to generate the link for
    :raises ExtensionError: if none of ``blob_url``, ``repo_url``, or ``context`` are provided
    """
    # """
    if blob_url is None:
        if repo_url is None:
            if context is None:
                raise ExtensionError(
                    "``sphinx_readme:`` config value ``html_context`` is missing")
            else:
                repo_url = get_repo_url(context)
        blob_url = get_blob_url(repo_url, blob, context)

    if 'bitbucket' in blob_url:
        return blob_url + "/{filepath}#lines-{linestart}:{linestop}"
    else:
        return blob_url + "/{filepath}#L{linestart}-L{linestop}"


def get_linkcode_resolve(linkcode_url: str) -> Callable:
    """Defines and returns a ``linkcode_resolve()`` function for your package

    :param linkcode_url: the template URL for linking to source code (see :meth:`~get_linkcode_url`)
    """
    repo_dir = get_repo_dir()

    def linkcode_resolve(domain, info):
        """Returns a link to the source code on GitHub, with appropriate lines highlighted

        :By:
            Adam Korn (https://github.com/tdkorn)
        :Adapted From:
            nlgranger/SeqTools (https://github.com/nlgranger/seqtools/blob/master/docs/conf.py)
        """
        if domain != 'py' or not info['module']:
            return None

        modname = info['module']
        fullname = info['fullname']

        submod = sys.modules.get(modname)
        if submod is None:
            return None

        obj = submod
        for part in fullname.split('.'):
            try:
                obj = getattr(obj, part)
            except AttributeError:
                return None

        if isinstance(obj, property):
            obj = obj.fget
        elif isinstance(obj, cached_property):
            obj = obj.func

        try:
            modpath = inspect.getsourcefile(inspect.unwrap(obj))
            filepath = Path(modpath).relative_to(repo_dir)
            if filepath is None:
                return
        except Exception:
            return None

        try:
            source, lineno = inspect.getsourcelines(obj)
        except Exception:
            return None

        linestart, linestop = lineno, lineno + len(source) - 1

        # Example: https://github.com/TDKorn/my-magento/blob/docs/magento/models/model.py#L28-L59
        final_link = linkcode_url.format(
            filepath=filepath.as_posix(),
            linestart=linestart,
            linestop=linestop
        )
        logger.debug(f"Final Link for {fullname}: {final_link}")
        return final_link

    return linkcode_resolve
