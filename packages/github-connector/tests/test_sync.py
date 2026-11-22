import httpx
import pytest
from aeo_github import GitHubClient, collect_repository_snapshot


@pytest.mark.asyncio
async def test_snapshot_collects_repository_ci_and_work_tracking_metadata() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        path = request.url.path
        if path == "/repos/example/project":
            return httpx.Response(
                200,
                json={
                    "id": 1,
                    "full_name": "example/project",
                    "private": False,
                    "default_branch": "main",
                    "updated_at": "2026-11-20T10:00:00Z",
                    "html_url": "https://github.com/example/project",
                },
            )
        if path.endswith("/commits"):
            return httpx.Response(200, json=[])
        if path.endswith("/pulls"):
            return httpx.Response(200, json=[])
        if path.endswith("/issues"):
            return httpx.Response(200, json=[{"number": 2, "title": "An issue", "updated_at": "2026-11-20T10:00:00Z", "html_url": "https://github.com/example/project/issues/2"}])
        if path.endswith("/actions/runs"):
            return httpx.Response(200, json={"workflow_runs": []})
        return httpx.Response(404)

    client = GitHubClient(None, transport=httpx.MockTransport(handler))
    try:
        records = await collect_repository_snapshot(client, "example/project")
    finally:
        await client.aclose()

    assert [record.event_type for record in records] == [
        "github.repository.snapshot",
        "github.issue.observed",
    ]
    assert all(record.classification == "public" for record in records)
    assert len(requests) == 5
    assert all(request.method == "GET" for request in requests)


def test_repository_slug_validation_rejects_path_traversal() -> None:
    from aeo_github.sync import validate_repository_slug

    with pytest.raises(ValueError):
        validate_repository_slug("example/../secrets")
