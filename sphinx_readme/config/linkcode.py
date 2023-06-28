import os
import re
import sys
import inspect
import subprocess
from pathlib import Path
from typing import Dict, Optional, Callable
from sphinx.errors import ExtensionError
from sphinx_readme.utils import logger


def get_linkcode_url(blob_url: Optional[str] = None,
                     repo_url: Optional[str] = None,
                     context: Optional[Dict] = None,
                     blob: Optional[str] = None) -> str:
    """Get the template URL for linking to highlighted GitHub source code

    Formatted into the final link by ``linkcode_resolve()``
    """
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


def get_repo_url(context: Dict):
    for host in ('github', 'gitlab', 'bitbucket'):
        user = context.get(f"{host}_user")
        repo = context.get(f"{host}_repo")

        if not all((user, repo)):
            continue

        tld = "org" if host == "bitbucket" else "com"
        return f"https://{host}.{tld}/{user}/{repo}"

    logger.error("``sphinx_readme``: unable to determine repo url")
    return None


def get_blob_url(repo_url: str, blob: Optional[str] = None, context: Optional[Dict] = None) -> str:
    """Generate the url for a specific blob of a repository

    If ``blob`` and ``context`` are not provided, the most recent commit hash will be used
    """
    host = get_repo_host(repo_url)

    if context:
        blob = context.get(f"{host}_version")

    if blob:
        # Use blob from kwarg/html_context
        blob = get_linkcode_revision(blob)

    else:
        # Use hash of the most recent commit
        blob = get_linkcode_revision('head')

    if host == "bitbucket":
        return repo_url.strip('/') + f"/src/{blob}"
    else:
        return repo_url.strip("/") + f"/blob/{blob}"


def get_repo_host(url: str):
    if match := re.match(r"https?://(\w+)\.(?:com|org)", url):
        return match.group(1)
    return None


def get_linkcode_revision(blob: str) -> str:
    """Get the blob to link to

    .. note::

       The value of ``blob`` can be any of ``"head"``, ``"last_tag"``, or ``"{blob}"``

       * ``head`` (default): links to the most recent commit hash; if this commit is tagged, uses the tag instead
       * ``last_tag``: links to the most recently tagged commit; if no tags exist, uses ``head``
       * ``blob``: links to any blob you want, for example ``"master"`` or ``"v2.0.1"``
    """
    if blob == "head":
        return get_head()
    if blob == 'last_tag':
        return get_last_tag()
    # Link to the branch/tree/blob you provided, ex. "master"
    return blob


def get_head(errors: bool = False) -> Optional[str]:
    """Gets the most recent commit hash or tag

    :raises subprocess.CalledProcessError: if the commit can't be found and ``errors`` is ``True``
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
        if errors:
            raise e
        else:
            return logger.error("Failed to get head")  # so no head?


def get_last_tag() -> str:
    """Get the most recent commit tag

    :raises RuntimeError: if there are no tagged commits
    """
    try:
        cmd = "git describe --tags --abbrev=0"
        return subprocess.check_output(cmd.split(" ")).strip().decode('utf-8')

    except subprocess.CalledProcessError as e:
        raise RuntimeError("No tags exist for the repo") from e


def get_linkcode_resolve(linkcode_url: str) -> Callable:
    """Defines and returns a ``linkcode_resolve`` function for your package

    Used by default if ``linkcode_resolve`` isn't defined in ``conf.py``
    """

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

        pkg_name = modname.split('.')[0]
        pkg_dir = sys.modules.get(pkg_name).__file__
        repo_dir = Path(pkg_dir).parent.parent

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
        filepath = '/'.join(filepath[filepath.find(pkg_name):].split('\\'))

        # Example: https://github.com/TDKorn/my-magento/blob/docs/magento/models/model.py#L28-L59
        final_link = linkcode_url.format(
            filepath=filepath,
            linestart=linestart,
            linestop=linestop
        )
        logger.debug(f"Final Link for {fullname}: {final_link}")
        return final_link

    return linkcode_resolve
