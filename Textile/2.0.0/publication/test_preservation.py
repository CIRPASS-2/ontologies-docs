"""Repository preservation under LF/CRLF, with committed and staged controls."""
import subprocess
import pytest
from validate import verify_repository_preservation


@pytest.fixture(params=['false', 'true'], ids=['LF-checkout', 'CRLF-checkout'])
def repository(tmp_path, request):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=tmp_path)
    git('init', '--quiet')
    git('config', '--local', 'core.autocrlf', request.param)
    git('config', '--local', 'core.eol', 'crlf' if request.param == 'true' else 'lf')
    git('config', '--local', 'user.name', 'Preservation test')
    git('config', '--local', 'user.email', 'test@example.invalid')
    (tmp_path / '.gitattributes').write_bytes(b'*.html text\n')
    folder = tmp_path / 'Battery'
    folder.mkdir()
    page = folder / 'index.html'
    page.write_bytes(b'<p>Preserved battery page</p>\n')
    git('add', '.gitattributes', 'Battery/index.html')
    git('commit', '--quiet', '-m', 'Baseline fixture')
    revision = git('rev-parse', 'HEAD').decode().strip()
    page.unlink()
    git('checkout-index', '--force', '--all')
    expected = b'<p>Preserved battery page</p>' + (b'\r\n' if request.param == 'true' else b'\n')
    assert page.read_bytes() == expected
    return tmp_path, revision, git


def test_accepts_unchanged_repository_in_lf_and_crlf_checkout(repository):
    root, revision, _ = repository
    assert verify_repository_preservation(root, revision) == 2


def test_rejects_unstaged_content_edit(repository):
    root, revision, _ = repository
    (root / 'Battery/index.html').write_bytes(b'<p>Altered battery page</p>\n')
    with pytest.raises(AssertionError, match='Protected unstaged content changed'):
        verify_repository_preservation(root, revision)


def test_rejects_staged_change_even_after_working_file_is_restored(repository):
    root, revision, git = repository
    page = root / 'Battery/index.html'
    preserved = page.read_bytes()
    page.write_bytes(b'<p>Unauthorized staged content</p>\n')
    git('add', 'Battery/index.html')
    page.write_bytes(preserved)
    with pytest.raises(AssertionError, match='Protected staged objects changed'):
        verify_repository_preservation(root, revision)


def test_rejects_committed_protected_change(repository):
    root, revision, git = repository
    (root / 'Battery/index.html').write_bytes(b'<p>Unauthorized committed content</p>\n')
    git('add', 'Battery/index.html')
    git('commit', '--quiet', '-m', 'Unauthorized fixture change')
    with pytest.raises(AssertionError, match='Protected committed objects changed'):
        verify_repository_preservation(root, revision)


def test_rejects_staged_protected_addition(repository):
    root, revision, git = repository
    (root / 'Battery/extra.html').write_bytes(b'Unauthorized addition\n')
    git('add', 'Battery/extra.html')
    with pytest.raises(AssertionError, match='Protected staged objects changed'):
        verify_repository_preservation(root, revision)


def test_rejects_staged_protected_deletion(repository):
    root, revision, git = repository
    git('update-index', '--force-remove', 'Battery/index.html')
    with pytest.raises(AssertionError, match='Protected staged objects changed'):
        verify_repository_preservation(root, revision)
