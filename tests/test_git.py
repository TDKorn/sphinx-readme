import pytest
from sphinx.errors import ExtensionError
from sphinx_readme.utils.git import get_repo_url, is_valid_username, is_valid_repo

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
def test_get_repo_url_invalid_user(html_context, host):
    """Integration test for ``is_valid_username()``"""
    invalid_context = html_context.copy()
    invalid_context[f'{host}_user'] = "invalid/user"

    with pytest.raises(ExtensionError, match=f"``sphinx_readme``: {host} username is invalid."):
        assert get_repo_url(invalid_context)


@pytest.mark.parametrize('html_context,host', zip(context_dicts, hosts))
def test_get_repo_url_missing_repo(html_context, host):
    html_context = html_context.copy()
    html_context.pop(f'{host}_repo')

    with pytest.raises(ExtensionError, match="``sphinx_readme``: unable to determine repo url"):
        assert get_repo_url(html_context)


@pytest.mark.parametrize('html_context,host', zip(context_dicts, hosts))
def test_get_repo_url_invalid_repo(html_context, host):
    """Integration test for ``is_valid_repo()``"""
    invalid_context = html_context.copy()
    invalid_context[f'{host}_repo'] = "invalid/repo"

    with pytest.raises(ExtensionError, match=f"``sphinx_readme``: {host} repo is invalid."):
        assert get_repo_url(invalid_context)


def test_get_repo_url_empty_dict():
    with pytest.raises(ExtensionError, match="``sphinx_readme``: unable to determine repo url"):
        assert get_repo_url({})


def test_get_repo_url_wrong_type():
    with pytest.raises(TypeError, match="``context`` must be a dictionary"):
        assert get_repo_url("html_context")


@pytest.mark.parametrize('username,host,expected', [
    # GitHub Test Cases
    ('x', 'github', True),  # minimum length
    ('x' * 39, 'github', True),  # maximum length
    ('validUser', 'github', True),
    ('validUser69', 'github', True),
    ('0000', 'github', True),
    ('valid-User', 'github', True),
    ('validUser-0', 'github', True),
    ('0-validUser', 'github', True),
    ('0-validUser-0', 'github', True),
    ('-invalidUser', 'github', False),
    ('invalidUser-', 'github', False),
    ('invalid-User-', 'github', False),
    ('invalid--User', 'github', False),
    ('invalid User', 'github', False),
    ('invalid/User', 'github', False),
    ('x' * 40, 'github', False),  # too long
    # GitLab Test Cases
    ('xx', 'gitlab', True),  # minimum length
    ('x' * 255, 'gitlab', True),  # maximum length
    ('validUser', 'gitlab', True),
    ('valid_User', 'gitlab', True),
    ('valid-User', 'gitlab', True),
    ('valid.User', 'gitlab', True),
    ('validUser69', 'gitlab', True),
    ('valid_User-69', 'gitlab', True),
    ('valid-User.69_420', 'gitlab', True),
    ('valid_User_69', 'gitlab', True),
    ('x', 'gitlab', False),  # too short
    ('x' * 256, 'gitlab', False),  # too long
    ('invalid User', 'gitlab', False),
    ('invalid/User_invalidUser', 'gitlab', False),
    ('.invalidUser', 'gitlab', False),
    ('-invalidUser', 'gitlab', False),
    ('invalidUser_', 'gitlab', False),
    ('invalidUser.', 'gitlab', False),
    ('invalidUser-', 'gitlab', False),
    ('invalid__User', 'gitlab', False),
    ('invalid_.User', 'gitlab', False),
    ('invalid_-User', 'gitlab', False),
    ('invalid._User', 'gitlab', False),
    ('invalid..User', 'gitlab', False),
    ('invalid.-User', 'gitlab', False),
    ('invalid-_User', 'gitlab', False),
    ('invalid-.User', 'gitlab', False),
    ('invalid--User', 'gitlab', False),
    # BitBucket Test Cases
    ('x', 'bitbucket', True),  # minimum length
    ('validUser', 'bitbucket', True),
    ('validUser69', 'bitbucket', True),
    ('0000', 'bitbucket', True),
    ('valid_User', 'bitbucket', True),
    ('valid-User', 'bitbucket', True),
    ('-validUser', 'bitbucket', True),
    ('_validUser', 'bitbucket', True),
    ('validUser-', 'bitbucket', True),
    ('validUser_', 'bitbucket', True),
    ('invalid User', 'bitbucket', False),
    ('invalid/User', 'bitbucket', False),
    # Invalid Host
    ("username", "random_website", False)
])
def test_is_valid_username(username, host, expected):
    assert is_valid_username(username, host) == expected


@pytest.mark.parametrize("repo, host, expected", [
    # GitHub Test Cases
    ("x", "github", True),  # minimum length
    ("x" * 100, "github", True),  # maximum length
    ("validrepo", "github", True),
    ("valid-repo", "github", True),
    ("valid_repo", "github", True),
    ("valid.repo", "github", True),
    ("0000000", "github", True),
    ("", "github", False),  # too short
    ("x" * 101, "github", False),  # too long
    ("invalid repo", "github", False),

    # GitLab Test Cases
    ("x", "gitlab", True),  # minimum length
    ("validrepo", "gitlab", True),
    ("valid69repo", "gitlab", True),
    ("valid-repo-", "gitlab", True),
    ("valid_repo_", "gitlab", True),
    ("valid.repo.", "gitlab", True),
    ("valid+repo+", "gitlab", True),
    ("valid repo", "gitlab", True),
    ("_validrepo", "gitlab", True),
    ("1validrepo", "gitlab", True),
    ("", "gitlab", False),  # too short
    ("-invalidrepo", "gitlab", False),
    (".invalidrepo", "gitlab", False),
    ("+invalidrepo", "gitlab", False),
    ("invalid/repo", "gitlab", False),

    # BitBucket Test Cases
    ("x", "bitbucket", True),  # minimum length
    ("x" * 62, "bitbucket", True),  # maximum length
    ("validrepo", "bitbucket", True),
    ("valid-repo", "bitbucket", True),
    ("valid_repo_", "bitbucket", True),
    ("valid.repo.", "bitbucket", True),
    ("69-validrepo", "bitbucket", True),
    ("_validrepo", "bitbucket", True),
    (".validrepo", "bitbucket", True),
    ("valid__repo", "bitbucket", True),
    ("valid..repo", "bitbucket", True),
    ("", "bitbucket", False),  # too short
    ("x" * 63, "bitbucket", False),  # too long
    ("-validrepo", "bitbucket", False),
    ("validrepo-", "bitbucket", False),
    ("valid--repo", "bitbucket", False),
    ("invalid repo", "bitbucket", False),

    # Invalid Host
    ("repo", "random_website", False)
])
def test_is_valid_repo(repo, host, expected):
    assert is_valid_repo(repo, host) == expected
