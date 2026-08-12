#!/usr/bin/env python3
"""Shared GitHub helpers for skill install scripts."""

from __future__ import annotations

import os
import urllib.parse
import urllib.request

# Hosts entitled to see the user's GitHub token. Archive downloads legitimately
# redirect from api.github.com to codeload.github.com and to
# objects.githubusercontent.com, so both domains (and their subdomains) count.
TRUSTED_HOST_SUFFIXES = ("github.com", "githubusercontent.com")

DEFAULT_TIMEOUT = 30


def is_trusted_url(url: str) -> bool:
    """True when *url* is an https GitHub URL that may receive credentials."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    return any(
        host == suffix or host.endswith("." + suffix)
        for suffix in TRUSTED_HOST_SUFFIXES
    )


def _strip_authorization(request: urllib.request.Request) -> None:
    for header in list(request.headers):
        if header.lower() == "authorization":
            del request.headers[header]
    for header in list(request.unredirected_hdrs):
        if header.lower() == "authorization":
            del request.unredirected_hdrs[header]


class _AuthScopingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Drop the Authorization header when a redirect leaves trusted GitHub hosts.

    urllib copies every header onto the redirect request, so without this a
    redirect to an attacker-controlled host would receive the user's token.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_request = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_request is not None and not is_trusted_url(new_request.full_url):
            _strip_authorization(new_request)
        return new_request


_opener = urllib.request.build_opener(_AuthScopingRedirectHandler)


def github_request(url: str, user_agent: str, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Refusing to request a non-https URL: {url}")

    headers = {"User-Agent": user_agent}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    # Only GitHub hosts get the credential; a non-GitHub URL is still fetched,
    # just anonymously.
    if token and is_trusted_url(url):
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with _opener.open(req, timeout=timeout) as resp:
        return resp.read()


def github_api_contents_url(repo: str, path: str, ref: str) -> str:
    repo = urllib.parse.quote(repo.strip("/"), safe="/")
    path = urllib.parse.quote(path.strip("/"), safe="/")
    ref = urllib.parse.quote(ref, safe="")
    return f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
