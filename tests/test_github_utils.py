"""Tests for skill-installer credential scoping."""

from __future__ import annotations

import email.message
import http.server
import importlib.util
import os
import sys
import threading
import urllib.request

import pytest

SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skill-installer",
    "scripts",
)
sys.path.insert(0, SCRIPTS)

import github_utils  # noqa: E402


def _load_installer():
    path = os.path.join(SCRIPTS, "install-skill-from-github.py")
    spec = importlib.util.spec_from_file_location("install_skill_from_github", path)
    module = importlib.util.module_from_spec(spec)
    # @dataclass resolves annotations through sys.modules, so register first.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


installer = _load_installer()


@pytest.mark.parametrize(
    "url, trusted",
    [
        ("https://github.com/owner/repo", True),
        ("https://api.github.com/repos/owner/repo", True),
        ("https://codeload.github.com/owner/repo/zip/main", True),
        ("https://objects.githubusercontent.com/blob", True),
        ("http://github.com/owner/repo", False),  # cleartext
        ("https://evil.com/owner/repo", False),
        ("https://github.com.evil.com/owner/repo", False),  # suffix look-alike
        ("https://notgithub.com/owner/repo", False),
        ("https://evil.com/?x=github.com", False),
        ("https://GITHUB.COM/owner/repo", True),  # host casing
    ],
)
def test_is_trusted_url(url, trusted):
    assert github_utils.is_trusted_url(url) is trusted


def _redirect(from_url, to_url):
    handler = github_utils._AuthScopingRedirectHandler()
    request = urllib.request.Request(
        from_url, headers={"Authorization": "token SECRET", "User-Agent": "test"}
    )
    new_request = handler.redirect_request(
        request, None, 302, "Found", email.message.Message(), to_url
    )
    assert new_request is not None
    return new_request


def test_redirect_off_github_strips_authorization():
    new_request = _redirect("https://api.github.com/repos/o/r", "https://evil.com/x")

    assert new_request.get_header("Authorization") is None
    assert new_request.get_header("User-agent") == "test"


def test_redirect_downgrade_to_http_strips_authorization():
    new_request = _redirect("https://api.github.com/repos/o/r", "http://github.com/x")

    assert new_request.get_header("Authorization") is None


def test_redirect_within_github_keeps_authorization():
    new_request = _redirect(
        "https://api.github.com/repos/o/r",
        "https://objects.githubusercontent.com/archive",
    )

    assert new_request.get_header("Authorization") == "token SECRET"


class _CapturingOpener:
    def __init__(self):
        self.request = None
        self.timeout = None

    def open(self, request, timeout=None):  # noqa: A003 - mirrors urllib's API
        self.request = request
        self.timeout = timeout
        return self

    def read(self):
        return b"payload"

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


@pytest.fixture
def capturing_opener(monkeypatch):
    opener = _CapturingOpener()
    monkeypatch.setattr(github_utils, "_opener", opener)
    monkeypatch.setenv("GITHUB_TOKEN", "SECRET")
    return opener


def test_token_is_sent_to_github(capturing_opener):
    assert github_utils.github_request("https://api.github.com/repos/o/r", "ua") == b"payload"

    assert capturing_opener.request.get_header("Authorization") == "token SECRET"
    assert capturing_opener.timeout == github_utils.DEFAULT_TIMEOUT


def test_token_is_withheld_from_non_github_hosts(capturing_opener):
    github_utils.github_request("https://evil.com/repos/o/r", "ua")

    assert capturing_opener.request.get_header("Authorization") is None


def test_gh_token_is_used_as_a_fallback(capturing_opener, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN")
    monkeypatch.setenv("GH_TOKEN", "FALLBACK")

    github_utils.github_request("https://api.github.com/repos/o/r", "ua")

    assert capturing_opener.request.get_header("Authorization") == "token FALLBACK"


def test_no_token_sends_no_authorization_header(capturing_opener, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN")
    monkeypatch.delenv("GH_TOKEN", raising=False)

    github_utils.github_request("https://api.github.com/repos/o/r", "ua")

    assert capturing_opener.request.get_header("Authorization") is None


@pytest.mark.parametrize("url", ["http://api.github.com/x", "file:///etc/passwd"])
def test_non_https_urls_are_refused(url, capturing_opener):
    with pytest.raises(ValueError):
        github_utils.github_request(url, "ua")

    assert capturing_opener.request is None


class _RedirectServer(http.server.BaseHTTPRequestHandler):
    """Redirects /start to a second server and records headers on arrival."""

    target = ""
    seen: dict = {}

    def do_GET(self):  # noqa: N802 - http.server API
        if self.path == "/start":
            self.send_response(302)
            self.send_header("Location", self.target)
            self.end_headers()
            return
        type(self).seen["authorization"] = self.headers.get("Authorization")
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def test_authorization_is_not_forwarded_across_a_real_redirect():
    """End-to-end regression test for the reported token leak."""
    seen: dict = {}

    class Handler(_RedirectServer):
        pass

    Handler.seen = seen

    first = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    second = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    Handler.target = f"http://127.0.0.1:{second.server_address[1]}/landing"

    for server in (first, second):
        threading.Thread(target=server.serve_forever, daemon=True).start()

    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{first.server_address[1]}/start",
            headers={"Authorization": "token SECRET", "User-Agent": "test"},
        )
        with github_utils._opener.open(request, timeout=10) as response:
            assert response.read() == b"ok"
    finally:
        for server in (first, second):
            server.shutdown()
            server.server_close()

    assert seen["authorization"] is None


def test_contents_url_encodes_user_input():
    url = github_utils.github_api_contents_url(
        "owner/repo", "skills/.curated", "feature branch"
    )

    assert url == (
        "https://api.github.com/repos/owner/repo/contents/skills/.curated"
        "?ref=feature%20branch"
    )


def test_contents_url_cannot_inject_query_parameters():
    url = github_utils.github_api_contents_url("owner/repo", "a?b=c#d", "main")

    assert url == (
        "https://api.github.com/repos/owner/repo/contents/a%3Fb%3Dc%23d?ref=main"
    )


def test_quote_ref_keeps_slashes_and_rejects_traversal():
    assert installer._quote_ref("feature/new thing") == "feature/new%20thing"

    for bad in ("../../x", "a/../b", "a//b", ""):
        with pytest.raises(installer.InstallError):
            installer._quote_ref(bad)


def test_quote_segment_encodes_separators():
    assert installer._quote_segment("owner/../evil") == "owner%2F..%2Fevil"

    with pytest.raises(installer.InstallError):
        installer._quote_segment("")
