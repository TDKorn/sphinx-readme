import pytest
from sphinx.errors import ExtensionError
from sphinx_readme.utils.git import get_repo_url

# GitHub Repo
github_html_context = {
    "github_user": "TDKorn",
    "github_repo": "sphinx-readme",
    "github_version": "main"
}
github_repo_url = "https://github.com/TDKorn/sphinx-readme"

# BitBucket Repo
bitbucket_html_context = {
    "bitbucket_user": "sphinx-readme",
    "bitbucket_repo": "sphinx-readme",
    "bitbucket_version": "master"
}
bitbucket_repo_url = "https://bitbucket.org/sphinx-readme/sphinx-readme"

# GitLab Repo
gitlab_html_context = {
    "gitlab_user": "sphinx_readme",
    "gitlab_repo": "readme",
    "gitlab_version": "master"
}
gitlab_repo_url = "https://gitlab.com/sphinx_readme/readme"

# Test Case Lists
context_dicts = [github_html_context, bitbucket_html_context, gitlab_html_context]
repo_urls = [github_repo_url, bitbucket_repo_url, gitlab_repo_url]
hosts = ['github', 'bitbucket', 'gitlab']


@pytest.mark.parametrize('html_context,repo_url', zip(context_dicts, repo_urls))
def test_get_repo_url(html_context, repo_url):
    assert get_repo_url(html_context) == repo_url


@pytest.mark.parametrize('html_context,host,repo_url', zip(context_dicts, hosts, repo_urls))
def test_get_repo_url_missing_version(html_context, host, repo_url):
    html_context = html_context.copy()
    html_context.pop(f'{host}_version')

    assert get_repo_url(html_context) == repo_url


@pytest.mark.parametrize('html_context,host', zip(context_dicts, hosts))
def test_get_repo_url_missing_user(html_context, host):
    html_context = html_context.copy()
    html_context.pop(f'{host}_user')

    with pytest.raises(ExtensionError, match="``sphinx_readme``: unable to determine repo url"):
        assert get_repo_url(html_context)


@pytest.mark.parametrize('html_context,host', zip(context_dicts, hosts))
def test_get_repo_url_missing_repo(html_context, host):
    html_context = html_context.copy()
    html_context.pop(f'{host}_repo')

    with pytest.raises(ExtensionError, match="``sphinx_readme``: unable to determine repo url"):
        assert get_repo_url(html_context)


def test_get_repo_url_empty_dict():
    with pytest.raises(ExtensionError, match="``sphinx_readme``: unable to determine repo url"):
        assert get_repo_url({})


def test_get_repo_url_wrong_type():
    with pytest.raises(TypeError, match="``context`` must be a dictionary"):
        assert get_repo_url("html_context")
