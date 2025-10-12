"""Helpers for authenticating as a GitHub App."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import jwt
import requests

GITHUB_API_URL = "https://api.github.com"


class GitHubAppAuthenticationError(RuntimeError):
    """Raised when authenticating as a GitHub App fails."""


def _normalize_private_key(raw_key: str) -> str:
    """Normalize private key contents taken from environment variables."""
    return raw_key.replace("\\n", "\n")


def load_private_key(
    *,
    private_key: Optional[str] = None,
    private_key_path: Optional[Path] = None,
) -> str:
    """Load a GitHub App private key from a string or a file."""
    if private_key and private_key_path:
        raise GitHubAppAuthenticationError(
            "provide either private key text or a path, not both"
        )

    if private_key_path is not None:
        return _normalize_private_key(private_key_path.read_text())

    if private_key is not None:
        return _normalize_private_key(private_key)

    raise GitHubAppAuthenticationError(
        "a GitHub App private key is required via --private-key or --private-key-path"
    )


def create_jwt(app_id: str, private_key: str) -> str:
    """Create a short-lived JWT for GitHub App authentication."""
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 9 * 60,
        "iss": app_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_token(
    *,
    app_id: str,
    installation_id: str,
    private_key: str,
    api_url: str = GITHUB_API_URL,
) -> str:
    """Retrieve an installation access token for a GitHub App."""
    token = create_jwt(app_id, private_key)
    url = f"{api_url}/app/installations/{installation_id}/access_tokens"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )
    if response.status_code != 201:
        raise GitHubAppAuthenticationError(
            f"failed to create installation token: {response.status_code} {response.text}"
        )
    data = response.json()
    try:
        return data["token"]
    except KeyError as exc:  # pragma: no cover - defensive
        raise GitHubAppAuthenticationError(
            "installation token response missing 'token'"
        ) from exc
