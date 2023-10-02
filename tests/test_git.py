import pytest
import subprocess
from unittest.mock import patch
from sphinx.errors import ExtensionError
from sphinx_readme.utils.git import get_repo_url, get_blob_url, is_valid_username, is_valid_repo, get_blob, get_head, get_last_tag

# GitHub Repo
github_html_context = {
    "github_user": "TDKorn",
    "github_repo": "sphinx-readme",
    "github_version": "master"
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
    ('valid-User', 'github', True),
    ('0-validUser-0', 'github', True),
    ('x' * 40, 'github', False),  # too long
    ('-invalidUser', 'github', False),
    ('invalidUser-', 'github', False),
    ('invalid--User', 'github', False),
    ('invalid User', 'github', False),

    # GitLab Test Cases
    ('xx', 'gitlab', True),  # minimum length
    ('x' * 255, 'gitlab', True),  # maximum length
    ('validUser', 'gitlab', True),
    ('valid-User.69_420', 'gitlab', True),
    ('x', 'gitlab', False),  # too short
    ('x' * 256, 'gitlab', False),  # too long
    ('_invalidUser', 'gitlab', False),
    ('.invalidUser', 'gitlab', False),
    ('-invalidUser', 'gitlab', False),
    ('invalidUser_', 'gitlab', False),
    ('invalidUser.', 'gitlab', False),
    ('invalidUser-', 'gitlab', False),
    ('invalid_.User', 'gitlab', False),
    ('invalid-_User', 'gitlab', False),
    ('invalid.-User', 'gitlab', False),
    ('invalid__User', 'gitlab', False),
    ('invalid..User', 'gitlab', False),
    ('invalid--User', 'gitlab', False),
    ('invalid User', 'gitlab', False),

    # BitBucket Test Cases
    ('x', 'bitbucket', True),  # minimum length
    ('validUser', 'bitbucket', True),
    ('0000', 'bitbucket', True),
    ('valid_User', 'bitbucket', True),
    ('valid-User', 'bitbucket', True),
    ('-validUser', 'bitbucket', True),
    ('_validUser', 'bitbucket', True),
    ('validUser-', 'bitbucket', True),
    ('validUser_', 'bitbucket', True),
    ('', 'bitbucket', False),  # too short
    ('invalid User', 'bitbucket', False),

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


blob_url_roots = [
    github_repo_url + "/blob/",
    bitbucket_repo_url + "/src/",
    gitlab_repo_url + "/blob/"
]
HEAD = "a5dea27ffabf340995348073d3a8ee14c0f6d693"
LAST_TAG = "v1.0.0"


@pytest.mark.parametrize('repo_url,blob_url_root', zip(repo_urls, blob_url_roots))
def test_get_blob_url_with_specific_blob(repo_url, blob_url_root):
    """If the blob name isn't ``head`` or ``last_tag``, the blob is used as is."""
    assert get_blob_url(repo_url, blob="tests") == blob_url_root + "tests"


@patch('sphinx_readme.utils.git.get_blob')
@pytest.mark.parametrize('repo_url,blob_url_root', zip(repo_urls, blob_url_roots))
def test_get_blob_url_with_head_blob(mocked_get_blob, repo_url, blob_url_root):
    """If the blob is ``"head"``, uses the name of the last tagged commit on the branch."""
    mocked_get_blob.return_value = HEAD

    assert get_blob_url(repo_url, blob="head") == blob_url_root + HEAD


@patch('sphinx_readme.utils.git.get_blob')
@pytest.mark.parametrize('repo_url,blob_url_root', zip(repo_urls, blob_url_roots))
def test_get_blob_url_with_last_tag_blob(mocked_get_blob, repo_url, blob_url_root):
    """If the blob is ``"last_tag"``, uses the name of the last tagged commit on the branch."""
    mocked_get_blob.return_value = LAST_TAG

    assert get_blob_url(repo_url, blob="last_tag") == blob_url_root + LAST_TAG


@pytest.mark.parametrize('repo_url,html_context,host,blob_url_root', zip(repo_urls, context_dicts, hosts, blob_url_roots))
def test_get_blob_url_with_valid_html_context(repo_url, html_context, host, blob_url_root):
    """If the ``html_context`` dict contains a version key, it should always be used as the blob."""
    expected = blob_url_root + html_context[f"{host}_version"]

    assert get_blob_url(repo_url, context=html_context) == expected
    assert get_blob_url(repo_url, context=html_context, blob="irrelevant") == expected


@patch('sphinx_readme.utils.git.get_blob')
@pytest.mark.parametrize('repo_url,blob_url_root', zip(repo_urls, blob_url_roots))
def test_get_blob_url_with_invalid_html_context(mocked_get_blob, repo_url, blob_url_root):
    """If ``html_context`` contains no valid version key or is the wrong type, ``"head"`` is used as the blob"""
    mocked_get_blob.return_value = HEAD
    expected = blob_url_root + HEAD

    assert get_blob_url(repo_url, context={}) == expected
    assert get_blob_url(repo_url, context="wrong_type") == expected
    assert get_blob_url(repo_url, context={"website_version": "master"}) == expected  # unsupported host


@pytest.mark.parametrize('repo_url,blob_url_root', zip(repo_urls, blob_url_roots))
def test_get_blob_url_with_invalid_html_context_and_blob(repo_url, blob_url_root):
    """If blob is provided and ``html_context`` contains no valid version key or is the wrong type, the blob is used"""
    blob = "some_blob"

    assert get_blob_url(repo_url, context={}, blob=blob) == blob_url_root + blob
    assert get_blob_url(repo_url, context="wrong_type", blob=blob) == blob_url_root + blob


@patch('sphinx_readme.utils.git.get_blob')
@pytest.mark.parametrize('repo_url,blob_url_root', zip(repo_urls, blob_url_roots))
def test_get_blob_url_with_no_html_context_or_blob(mocked_get_blob, repo_url, blob_url_root):
    """If no blob or html_context is provided, ``"head"`` is should be used as the blob"""
    mocked_get_blob.return_value = HEAD

    assert get_blob_url(repo_url) == blob_url_root + HEAD


@patch('sphinx_readme.utils.git.get_head')
def test_get_blob_url_runtime_error_from_get_head(mocked_get_head):
    mocked_get_head.side_effect = RuntimeError("Failed to get head")

    with pytest.raises(RuntimeError, match="Failed to get head"):
        get_blob_url(github_repo_url, blob="head")


@patch('sphinx_readme.utils.git.get_last_tag')
def test_get_blob_url_runtime_error_from_get_last_tag(mocked_get_last_tag):
    mocked_get_last_tag.side_effect = RuntimeError("No tags exist for the repo")

    with pytest.raises(RuntimeError, match="No tags exist for the repo"):
        get_blob_url(github_repo_url, blob="last_tag")


@patch('sphinx_readme.utils.git.get_head')
def test_get_blob_head(mocked_get_head):
    mocked_get_head.return_value = HEAD

    assert get_blob("head") == HEAD


@patch('sphinx_readme.utils.git.get_last_tag')
def test_get_blob_last_tag(mocked_get_last_tag):
    mocked_get_last_tag.return_value = LAST_TAG

    assert get_blob("last_tag") == LAST_TAG


def test_get_blob_specific_blob():
    assert get_blob("some_blob") == "some_blob"


@patch('sphinx_readme.utils.git.get_head')
def test_get_blob_runtime_error_from_get_head(mocked_get_head):
    mocked_get_head.side_effect = RuntimeError("Failed to get head")

    with pytest.raises(RuntimeError, match="Failed to get head"):
        get_blob("head")


@patch('sphinx_readme.utils.git.get_last_tag')
def test_get_blob_runtime_error_from_get_last_tag(mocked_get_last_tag):
    mocked_get_last_tag.side_effect = RuntimeError("No tags exist for the repo")

    with pytest.raises(RuntimeError, match="No tags exist for the repo"):
        get_blob("last_tag")


@patch('subprocess.check_output')
def test_get_head_not_tagged(mock_check_output):
    """If the most recent commit is not tagged, the SHA should be returned"""
    mock_check_output.side_effect = [f"{HEAD}\n".encode('utf-8'), subprocess.CalledProcessError(1, 'cmd')]

    assert get_head() == HEAD


@patch('subprocess.check_output')
def test_get_head_tagged(mock_check_output):
    """If the most recent commit *is* tagged, the tag name should be returned"""
    mock_check_output.side_effect = [f"{HEAD}\n".encode('utf-8'), f"{LAST_TAG}\n".encode('utf-8')]

    assert get_head() == LAST_TAG


@patch('subprocess.check_output')
def test_get_head_fails(mock_check_output):
    """Test when git command execution fails"""
    mock_check_output.side_effect = subprocess.CalledProcessError(1, 'cmd')

    with pytest.raises(RuntimeError, match="Failed to get head"):
        get_head()


@patch('subprocess.check_output')
def test_get_last_tag(mock_check_output):
    mock_check_output.return_value = f"{LAST_TAG}\n".encode('utf-8')

    assert get_last_tag() == LAST_TAG


@patch('subprocess.check_output')
def test_get_last_tag_fails(mock_check_output):
    """Test when git command execution fails/the current branch of the repo has no tags"""
    mock_check_output.side_effect = subprocess.CalledProcessError(1, 'cmd')

    with pytest.raises(RuntimeError, match="No tags exist for the repo"):
        get_last_tag()


