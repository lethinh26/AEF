from datetime import datetime
from urllib.parse import quote

from aeo_github.client import GitHubClient
from aeo_github.normalize import (
    NormalizedObservation,
    normalize_commit,
    normalize_issue,
    normalize_pull_request,
    normalize_repository,
    normalize_workflow_run,
)


def validate_repository_slug(value: str) -> tuple[str, str]:
    parts = value.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Repository must use the owner/repository format")
    owner, repository = parts
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    if not owner or not repository or any(char not in allowed for char in owner + repository):
        raise ValueError("Repository slug contains unsupported characters")
    return owner, repository


async def collect_repository_snapshot(
    client: GitHubClient,
    repository_slug: str,
    *,
    since: datetime | None = None,
) -> list[NormalizedObservation]:
    owner, repository = validate_repository_slug(repository_slug)
    owner_path = quote(owner, safe="")
    repository_path = quote(repository, safe="")
    prefix = f"/repos/{owner_path}/{repository_path}"
    per_page = 100

    repository_data = await client.get_json(prefix)
    commits_params: dict[str, str | int] = {"per_page": per_page}
    if since is not None:
        commits_params["since"] = since.isoformat()

    commits = await client.get_json(f"{prefix}/commits", params=commits_params)
    pulls = await client.get_json(
        f"{prefix}/pulls",
        params={"state": "all", "sort": "updated", "direction": "desc", "per_page": per_page},
    )
    issues = await client.get_json(
        f"{prefix}/issues",
        params={"state": "all", "sort": "updated", "direction": "desc", "per_page": per_page},
    )
    workflow_response = await client.get_json(
        f"{prefix}/actions/runs", params={"per_page": per_page}
    )

    if not isinstance(repository_data, dict):
        raise ValueError("GitHub repository endpoint returned an invalid payload")
    if not all(isinstance(items, list) for items in (commits, pulls, issues)):
        raise ValueError("GitHub list endpoint returned an invalid payload")
    workflow_runs = workflow_response.get("workflow_runs", [])
    if not isinstance(workflow_runs, list):
        raise ValueError("GitHub Actions endpoint returned an invalid payload")

    classification = "internal" if repository_data.get("private") else "public"
    observations = [normalize_repository(repository_data)]
    observations.extend(
        normalize_commit(item, classification=classification)
        for item in commits
        if isinstance(item, dict)
    )
    observations.extend(
        normalize_pull_request(item, classification=classification)
        for item in pulls
        if isinstance(item, dict)
    )
    observations.extend(
        normalize_issue(item, classification=classification)
        for item in issues
        if isinstance(item, dict) and "pull_request" not in item
    )
    observations.extend(
        normalize_workflow_run(item, classification=classification)
        for item in workflow_runs
        if isinstance(item, dict)
    )
    return observations
