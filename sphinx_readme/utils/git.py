import re
import subprocess
from pathlib import Path
from subprocess import DEVNULL
from typing import Dict, Optional
from sphinx.errors import ExtensionError


def get_repo_url(context: Dict) -> str:
    """Parses the repository URL from the Sphinx :external+sphinx:confval:`html_context` dict

    :param context: the ``html_context`` dict
    :return: the base URL of the project's repository
    :raises ExtensionError: if the repository URL cannot be parsed from ``html_context``
    """
    if not isinstance(context, dict):
        raise TypeError("``context`` must be a dictionary")

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
    if isinstance(context, dict):
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
            tag = subprocess.check_output(cmd.split(" "), stderr=DEVNULL).strip().decode('utf-8')
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
    if repo_dir.parent.stem == "checkouts":
        return repo_dir.parent.parent
    else:
        return repo_dir
