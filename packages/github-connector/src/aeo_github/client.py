from collections.abc import Mapping
from typing import Any

import httpx

GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"


class GitHubAPIError(RuntimeError):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.retry_after_seconds = retry_after_seconds


class GitHubClient:
    """A deliberately read-only GitHub REST client. It exposes GET and no write methods."""

    def __init__(
        self,
        token: str | None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout_seconds: float = 20.0,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "AEO-Shadow-Observer/0.1",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=GITHUB_API_BASE_URL,
            headers=headers,
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=False,
            transport=transport,
        )

    async def get_json(
        self, path: str, *, params: Mapping[str, str | int] | None = None
    ) -> Any:
        if not path.startswith("/repos/") or ".." in path.split("/"):
            raise ValueError("GitHub API path is outside the repository read boundary")

        response = await self._client.get(path, params=params)
        if response.is_error:
            remaining = response.headers.get("X-RateLimit-Remaining")
            retry_after = response.headers.get("Retry-After")
            if response.status_code == 403 and remaining == "0":
                code = "github_rate_limited"
            elif response.status_code == 401:
                code = "github_authentication_failed"
            elif response.status_code == 403:
                code = "github_permission_denied"
            elif response.status_code == 404:
                code = "github_resource_not_found"
            elif response.status_code >= 500:
                code = "github_upstream_unavailable"
            else:
                code = "github_api_request_failed"
            try:
                retry_after_seconds = int(retry_after) if retry_after else None
            except ValueError:
                retry_after_seconds = None
            raise GitHubAPIError(
                status_code=response.status_code,
                code=code,
                retry_after_seconds=retry_after_seconds,
            )
        return response.json()

    async def aclose(self) -> None:
        await self._client.aclose()
