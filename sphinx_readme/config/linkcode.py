import os
import re
import sys
import inspect
import subprocess
import pkg_resources
from pathlib import Path
from typing import Dict, Optional, Callable
from sphinx.errors import ExtensionError
from sphinx_readme.utils import logger


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


def get_repo_url(context: Dict) -> str:
    """Parses the repository URL from the Sphinx :external+sphinx:confval:`html_context` dict

    :param context: the ``html_context`` dict
    :return: the base URL of the project's repository
    :raises ExtensionError: if the repository URL cannot be parsed from ``html_context``
    """
    for host in ('github', 'gitlab', 'bitbucket'):
        user = context.get(f"{host}_user")
        repo = context.get(f"{host}_repo")

        if not all((user, repo)):
            continue

        if host == "bitbucket":
            tld = "org"
        else:
            tld = "com"

        return f"https://{host}.{tld}/{user}/{repo}"

    raise ExtensionError(
        "``sphinx_readme``: unable to determine repo url")


def get_blob_url(repo_url: str, blob: Optional[str] = None, context: Optional[Dict] = None) -> str:
    """Generates the base URL for a specific blob of a repository

    :param repo_url: the base URL of the repository
    :param blob: the blob of the repository to generate the link for
    :param context: the Sphinx :external+sphinx:confval:`html_context` dict
    """
    if context:
        host = get_repo_host(repo_url)
        blob = context.get(f"{host}_version")

    if blob is not None:
        # Use blob from kwarg/html_context
        blob = get_blob(blob)
    else:
        # Use hash of the most recent commit
        blob = get_blob('head')

    if "bitbucket" in repo_url:
        return repo_url.strip('/') + f"/src/{blob}"
    else:
        return repo_url.strip("/") + f"/blob/{blob}"


def get_repo_host(repo_url: str) -> Optional[str]:
    """Returns the hosting platform of a repository

    >>> get_repo_host("https://github.com/TDKorn/sphinx-readme")
    'github'

    :param repo_url: the URL of the repository
    """
    if match := re.match(r"https?://(\w+)\.(?:com|org)", repo_url):
        return match.group(1)
    return None


def get_blob(blob: str) -> str:
    """Returns the git blob corresponding to ``blob``

    The value of ``blob`` can be any of ``"head"``, ``"last_tag"``, or ``"{blob}"``

    * ``"head"``: returns the hash of the most recent commit; if this commit is tagged, uses the tag instead
    * ``"last_tag"``: returns the most recent commit tag; if no tags exist, uses ``"head"``
    * ``"{blob}"``: returns the specified blob as is, for example ``"master"`` or ``"v2.0.1"``
    """
    if blob == "head":
        return get_head()
    if blob == 'last_tag':
        return get_last_tag()
    # Return the branch/tree/blob you provided
    return blob


def get_head() -> str:
    """Returns the hash of the most recent commit

    If the most recent commit is tagged, the tag is returned instead

    :raises RuntimeError: if the most recent commit can't be found
    """
    cmd = "git log -n1 --pretty=%H"
    try:
        # get most recent commit hash
        head = subprocess.check_output(cmd.split()).strip().decode('utf-8')

        # if head is a tag, use tag as reference
        cmd = "git describe --exact-match --tags " + head
        try:
            tag = subprocess.check_output(cmd.split(" ")).strip().decode('utf-8')
            return tag

        except subprocess.CalledProcessError:
            return head

    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to get head") from e  # so no head?


def get_last_tag() -> str:
    """Returns the most recent commit tag

    :raises RuntimeError: if there are no tagged commits
    """
    try:
        cmd = "git describe --tags --abbrev=0"
        return subprocess.check_output(cmd.split(" ")).strip().decode('utf-8')

    except subprocess.CalledProcessError as e:
        raise RuntimeError("No tags exist for the repo") from e


def get_repo_dir() -> Path:
    """Returns the root directory of the repository

    :raises RuntimeError: if the directory can't be determined
    """
    try:
        cmd = "git rev-parse --show-toplevel"
        repo_dir = Path(subprocess.check_output(cmd.split(" ")).strip().decode('utf-8'))

    except subprocess.CalledProcessError as e:
        raise RuntimeError("Unable to determine the repository directory") from e

    # For ReadTheDocs, repo is cloned to /path/to/<repo_dir>/checkouts/<version>/
    if repo_dir.parent == "checkouts":
        return repo_dir.parent.parent
    else:
        return repo_dir


def get_linkcode_resolve(linkcode_url: str) -> Callable:
    """Defines and returns a ``linkcode_resolve()`` function for your package

    :param linkcode_url: the template URL for linking to source code (see :meth:`~get_linkcode_url`)
    """
    repo_dir = get_repo_dir()
    pkg = pkg_resources.require(repo_dir.name)[0]
    top_level = pkg.get_metadata('top_level.txt').strip()

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

        try:
            filepath = os.path.relpath(inspect.getsourcefile(obj), repo_dir)
            if filepath is None:
                return
        except Exception:
            return None

        try:
            source, lineno = inspect.getsourcelines(obj)
        except OSError:
            return None
        else:
            linestart, linestop = lineno, lineno + len(source) - 1

        # Fix links with "../../../" or "..\\..\\..\\"
        filepath = '/'.join(filepath[filepath.find(top_level):].split('\\'))

        # Example: https://github.com/TDKorn/my-magento/blob/docs/magento/models/model.py#L28-L59
        final_link = linkcode_url.format(
            filepath=filepath,
            linestart=linestart,
            linestop=linestop
        )
        logger.debug(f"Final Link for {fullname}: {final_link}")
        return final_link

    return linkcode_resolve
