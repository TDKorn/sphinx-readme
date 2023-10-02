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

        if not is_valid_username(user, host):
            raise ExtensionError(
                f"``sphinx_readme``: {host} username is invalid.")

        if not is_valid_repo(repo, host):
            raise ExtensionError(
                f"``sphinx_readme``: {host} repo is invalid.")

        if host == "bitbucket":
            tld = "org"
        else:
            tld = "com"

        return f"https://{host}.{tld}/{user}/{repo}"

    raise ExtensionError(
        "``sphinx_readme``: unable to determine repo url")


def is_valid_username(username: str, host: str) -> bool:
    """Validates a username on the given hosting platform.

    .. admonition:: **Username Constraints**
       :class: tip

       :GitHub:
          Usernames can only contain alphanumeric characters and hyphens; can't start or end with a hyphen or
          have consecutive hyphens; must be between 1 and 39 characters long.
       :GitLab:
          Usernames can only contain alphanumeric characters, underscores, hyphens, and periods;
          can't start or end with special characters or contain consecutive special characters;
          must be between 2 and 255 characters long.
       :BitBucket:
          Usernames can only contain alphanumeric characters, hyphens, and underscores.

    :param username: the username to validate.
    :param host: the platform where the repository is hosted.
    :return: True if the username is valid for the given platform, otherwise False.
    """
    if host == 'github':
        return bool(re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$", username))
    elif host == 'gitlab':
        return bool(re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|[_.-](?=[a-zA-Z0-9])){1,254}$", username))
    elif host == 'bitbucket':
        return bool(re.match(r'^[\w-]+$', username))
    else:
        return False


def is_valid_repo(repo: str, host: str) -> bool:
    """Validates the name of a git repository on the given hosting platform.

    .. admonition:: **Repository Name Constraints**
       :class: tip

       :GitHub:
          Repository names can only contain alphanumeric characters, hyphens, underscores, and periods;
          must be between 1 and 100 characters long.
       :GitLab:
          Repository name can only contain alphanumeric characters, hyphens, underscores, periods, "+", or spaces.
          It must start with a letter, digit, or '_' and be at least 1 character long.
       :BitBucket:
          Repository name can only contain alphanumeric characters, hyphens, underscores, and periods.
          It must start with an alphanumeric character, underscore or period and can't have consecutive
          hyphens or end with a hyphen. Must be between 1 and 62 characters long.

    :param repo: the name of the repository.
    :param host: the platform where the repository is hosted.
    :return: True if the repository name is valid, otherwise False.
    """
    if host == "github":
        return bool(re.match(r"^[\w.-]{1,100}$", repo))
    elif host == "gitlab":
        return bool(re.match(r"^\w[\w.+ -]*$", repo))
    elif host == "bitbucket":
        return bool(re.match(r"^[\w.](?:[\w.]|-(?=[\w.])){0,61}$", repo))
    else:
        return False


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
