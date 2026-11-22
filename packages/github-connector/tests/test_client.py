import httpx
import pytest
from aeo_github import GitHubAPIError, GitHubClient


@pytest.mark.asyncio
async def test_client_uses_get_and_attaches_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.host == "api.github.com"
        assert request.headers["Authorization"] == "Bearer test-read-only-token"
        return httpx.Response(200, json={"ok": True})

    client = GitHubClient("test-read-only-token", transport=httpx.MockTransport(handler))
    try:
        assert await client.get_json("/repos/example/project") == {"ok": True}
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_client_rejects_paths_outside_repository_api() -> None:
    client = GitHubClient(None, transport=httpx.MockTransport(lambda _: httpx.Response(200)))
    try:
        with pytest.raises(ValueError):
            await client.get_json("/user")
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_client_classifies_missing_permissions_without_response_body() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"message": "sensitive upstream response"})

    client = GitHubClient("token", transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(GitHubAPIError) as raised:
            await client.get_json("/repos/example/project")
        assert raised.value.code == "github_permission_denied"
        assert "sensitive upstream response" not in str(raised.value)
    finally:
        await client.aclose()
