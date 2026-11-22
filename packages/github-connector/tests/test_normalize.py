from aeo_github.normalize import normalize_issue, normalize_workflow_run, sanitize_text


def test_issue_normalization_redacts_secrets_and_personal_email() -> None:
    item = {
        "number": 17,
        "title": "Checkout retries fail",
        "body": "Please use api_key=super-secret-value and contact dev@example.com",
        "state": "open",
        "created_at": "2026-11-20T10:00:00Z",
        "updated_at": "2026-11-21T10:00:00Z",
        "html_url": "https://github.com/example/project/issues/17",
        "user": {"login": "contributor"},
        "labels": [{"name": "bug"}],
    }

    observation = normalize_issue(item)

    assert observation.source_event_id == "issue:17:2026-11-21T10:00:00Z"
    assert observation.event_type == "github.issue.observed"
    assert "super-secret-value" not in observation.payload["body"]
    assert "dev@example.com" not in observation.payload["body"]
    assert observation.payload["labels"] == ["bug"]


def test_workflow_run_normalization_preserves_ci_outcome() -> None:
    observation = normalize_workflow_run(
        {
            "id": 123,
            "run_number": 8,
            "run_attempt": 2,
            "name": "Backend CI",
            "status": "completed",
            "conclusion": "failure",
            "head_branch": "main",
            "head_sha": "abc123",
            "created_at": "2026-11-20T10:00:00Z",
            "updated_at": "2026-11-20T10:05:00Z",
            "html_url": "https://github.com/example/project/actions/runs/123",
        }
    )

    assert observation.payload["conclusion"] == "failure"
    assert observation.payload["run_attempt"] == 2
    assert observation.external_url.endswith("/123")


def test_text_redactor_handles_github_tokens_and_bearer_values() -> None:
    value = (
        "ghp_123456789012345678901234567890123456 and "
        "Bearer abcdefghijklmnopqrstuvwxyz and sk-123456789012345678901234"
    )
    redacted = sanitize_text(value)
    assert "ghp_" not in redacted
    assert "abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "sk-123456789012345678901234" not in redacted
