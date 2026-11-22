import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

SECRET_ASSIGNMENT = re.compile(
    r"(?i)(\b(?:api[_-]?key|access[_-]?token|token|secret|password|authorization)\b\s*[:=]\s*)"
    r"([^\s,;]+)"
)
GITHUB_TOKEN = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}")
COMMON_SECRET = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"AIza[0-9A-Za-z_-]{35})\b"
)
EMAIL_ADDRESS = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


@dataclass(frozen=True)
class NormalizedObservation:
    source_event_id: str
    event_type: str
    title: str
    summary: str
    external_url: str | None
    occurred_at: datetime | None
    classification: str
    payload: dict[str, Any]


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def sanitize_text(value: str | None, *, limit: int = 4_000) -> str:
    if not value:
        return ""
    sanitized = SECRET_ASSIGNMENT.sub(r"\1[REDACTED]", value)
    sanitized = GITHUB_TOKEN.sub("[REDACTED_TOKEN]", sanitized)
    sanitized = BEARER_TOKEN.sub("Bearer [REDACTED]", sanitized)
    sanitized = COMMON_SECRET.sub("[REDACTED_SECRET]", sanitized)
    sanitized = EMAIL_ADDRESS.sub("[REDACTED_EMAIL]", sanitized)
    return sanitized[:limit]


def _github_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme == "https" and parsed.hostname == "github.com":
        return value[:1024]
    return None


def _labels(item: dict[str, Any]) -> list[str]:
    labels = item.get("labels") or []
    return [sanitize_text(label.get("name"), limit=100) for label in labels if label.get("name")]


def normalize_repository(repository: dict[str, Any]) -> NormalizedObservation:
    full_name = repository.get("full_name") or "unknown/unknown"
    updated_at = repository.get("updated_at")
    private = bool(repository.get("private"))
    payload = {
        "kind": "repository",
        "id": repository.get("id"),
        "full_name": full_name,
        "private": private,
        "default_branch": repository.get("default_branch"),
        "description": sanitize_text(repository.get("description"), limit=1_000),
        "language": repository.get("language"),
        "archived": bool(repository.get("archived")),
        "fork": bool(repository.get("fork")),
        "created_at": repository.get("created_at"),
        "updated_at": updated_at,
        "pushed_at": repository.get("pushed_at"),
        "open_issues_count": repository.get("open_issues_count"),
        "stargazers_count": repository.get("stargazers_count"),
        "forks_count": repository.get("forks_count"),
        "html_url": _github_url(repository.get("html_url")),
    }
    return NormalizedObservation(
        source_event_id=f"repository:{repository.get('id')}:{updated_at or 'unknown'}",
        event_type="github.repository.snapshot",
        title=full_name,
        summary=sanitize_text(repository.get("description"), limit=500)
        or f"GitHub repository snapshot; default branch: {repository.get('default_branch', 'unknown')}",
        external_url=payload["html_url"],
        occurred_at=parse_timestamp(updated_at),
        classification="internal" if private else "public",
        payload=payload,
    )


def normalize_commit(
    item: dict[str, Any], *, classification: str = "internal"
) -> NormalizedObservation:
    commit = item.get("commit") or {}
    message = sanitize_text(commit.get("message"), limit=4_000)
    title = message.splitlines()[0][:500] if message else "Commit observed"
    author = commit.get("author") or {}
    github_author = item.get("author") or {}
    sha = item.get("sha") or "unknown"
    payload = {
        "kind": "commit",
        "sha": sha,
        "message": message,
        "author_name": sanitize_text(author.get("name"), limit=120),
        "author_login": sanitize_text(github_author.get("login"), limit=120),
        "committed_at": author.get("date"),
        "html_url": _github_url(item.get("html_url")),
        "parent_count": len(item.get("parents") or []),
    }
    return NormalizedObservation(
        source_event_id=f"commit:{sha}",
        event_type="github.commit.observed",
        title=title,
        summary=message[:1_000],
        external_url=payload["html_url"],
        occurred_at=parse_timestamp(author.get("date")),
        classification=classification,
        payload=payload,
    )


def normalize_pull_request(
    item: dict[str, Any], *, classification: str = "internal"
) -> NormalizedObservation:
    number = item.get("number")
    updated_at = item.get("updated_at")
    title = sanitize_text(item.get("title"), limit=500) or f"Pull request #{number}"
    body = sanitize_text(item.get("body"), limit=4_000)
    user = item.get("user") or {}
    payload = {
        "kind": "pull_request",
        "number": number,
        "title": title,
        "body": body,
        "state": item.get("state"),
        "draft": bool(item.get("draft")),
        "merged_at": item.get("merged_at"),
        "created_at": item.get("created_at"),
        "updated_at": updated_at,
        "closed_at": item.get("closed_at"),
        "author_login": sanitize_text(user.get("login"), limit=120),
        "labels": _labels(item),
        "comments": item.get("comments", 0),
        "review_comments": item.get("review_comments", 0),
        "head_ref": sanitize_text((item.get("head") or {}).get("ref"), limit=250),
        "base_ref": sanitize_text((item.get("base") or {}).get("ref"), limit=250),
        "head_sha": (item.get("head") or {}).get("sha"),
        "html_url": _github_url(item.get("html_url")),
    }
    return NormalizedObservation(
        source_event_id=f"pull_request:{number}:{updated_at or 'unknown'}",
        event_type="github.pull_request.observed",
        title=title,
        summary=body[:1_000] or f"Pull request #{number} · {item.get('state', 'unknown')}",
        external_url=payload["html_url"],
        occurred_at=parse_timestamp(updated_at or item.get("created_at")),
        classification=classification,
        payload=payload,
    )


def normalize_issue(
    item: dict[str, Any], *, classification: str = "internal"
) -> NormalizedObservation:
    number = item.get("number")
    updated_at = item.get("updated_at")
    title = sanitize_text(item.get("title"), limit=500) or f"Issue #{number}"
    body = sanitize_text(item.get("body"), limit=4_000)
    user = item.get("user") or {}
    payload = {
        "kind": "issue",
        "number": number,
        "title": title,
        "body": body,
        "state": item.get("state"),
        "created_at": item.get("created_at"),
        "updated_at": updated_at,
        "closed_at": item.get("closed_at"),
        "author_login": sanitize_text(user.get("login"), limit=120),
        "labels": _labels(item),
        "comments": item.get("comments", 0),
        "html_url": _github_url(item.get("html_url")),
    }
    return NormalizedObservation(
        source_event_id=f"issue:{number}:{updated_at or 'unknown'}",
        event_type="github.issue.observed",
        title=title,
        summary=body[:1_000] or f"Issue #{number} · {item.get('state', 'unknown')}",
        external_url=payload["html_url"],
        occurred_at=parse_timestamp(updated_at or item.get("created_at")),
        classification=classification,
        payload=payload,
    )


def normalize_workflow_run(
    item: dict[str, Any], *, classification: str = "internal"
) -> NormalizedObservation:
    run_id = item.get("id")
    attempt = item.get("run_attempt", 1)
    updated_at = item.get("updated_at")
    name = sanitize_text(item.get("name"), limit=300) or "GitHub Actions run"
    conclusion = item.get("conclusion") or item.get("status") or "unknown"
    payload = {
        "kind": "workflow_run",
        "id": run_id,
        "run_number": item.get("run_number"),
        "run_attempt": attempt,
        "name": name,
        "event": item.get("event"),
        "status": item.get("status"),
        "conclusion": conclusion,
        "head_branch": sanitize_text(item.get("head_branch"), limit=250),
        "head_sha": item.get("head_sha"),
        "created_at": item.get("created_at"),
        "updated_at": updated_at,
        "run_started_at": item.get("run_started_at"),
        "html_url": _github_url(item.get("html_url")),
    }
    return NormalizedObservation(
        source_event_id=f"workflow_run:{run_id}:{attempt}:{updated_at or 'unknown'}",
        event_type="github.workflow_run.observed",
        title=f"{name} · {conclusion}",
        summary=(
            f"Workflow {name} finished with {conclusion} on "
            f"{payload['head_branch'] or 'unknown branch'}"
        ),
        external_url=payload["html_url"],
        occurred_at=parse_timestamp(updated_at or item.get("created_at")),
        classification=classification,
        payload=payload,
    )
