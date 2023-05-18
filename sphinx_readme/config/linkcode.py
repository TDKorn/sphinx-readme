import inspect
import os
import subprocess
import sys
from pathlib import Path
from typing import Union, List, Dict, Optional, Callable
from sphinx.errors import ExtensionError
from sphinx_readme.utils import logger


def get_linkcode_url(blob: Optional[str] = None, context: Optional[Dict] = None, url: Optional[str] = None) -> str:
    """Get the template URL for linking to highlighted GitHub source code

    Formatted into the final link by ``linkcode_resolve()``
    """
    if url is None:
        if context is None or not all(context.get(key) for key in ("github_user", "github_repo")):
            raise ExtensionError(
                "``sphinx_readme:`` config value ``linkcode_url`` is missing")
        else:
            logger.info(
                "``sphinx_readme``: config value ``linkcode_url`` is missing. "
                "Creating link from ``html_context`` values..."
            )
            url = f"https://github.com/{context['github_user']}/{context['github_repo']}"

    blob = get_linkcode_revision(blob) if blob else context.get('github_version')

    if blob is not None:
        url = url.strip("/") + f"/blob/{blob}/"  # URL should be "https://github.com/user/repo"
    else:
        raise ExtensionError(
            "``sphinx_readme:`` must provide a blob or GitHub version to link to")

    return url + "{filepath}#L{linestart}-L{linestop}"


def get_linkcode_revision(blob: str) -> str:
    """Get the blob to link to on GitHub

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
            return print("Failed to get head")  # so no head?


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
        print(f"Final Link for {fullname}: {final_link}")
        return final_link

    return linkcode_resolve
