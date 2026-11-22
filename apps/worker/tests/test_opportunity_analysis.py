from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from aeo_worker.opportunity_analysis import (
    _evidence_id,
    _fingerprint,
    build_ci_failure_clusters,
    ci_failure_score,
    ci_failure_severity,
)


def make_observation(asset_id, workflow, branch, index):
    return SimpleNamespace(
        id=uuid4(),
        asset_id=asset_id,
        occurred_at=datetime.now(UTC) - timedelta(hours=index),
        summary=f"Workflow {workflow} finished with failure on {branch}",
    )


def test_ci_failure_clusters_require_repeated_signal_and_keep_branch_evidence() -> None:
    asset_id = uuid4()
    observations = [
        make_observation(asset_id, "Backend CI", "main", 1),
        make_observation(asset_id, "Backend CI", "release", 2),
        make_observation(asset_id, "Backend CI", "main", 3),
        make_observation(asset_id, "Frontend CI", "main", 1),
        make_observation(asset_id, "Frontend CI", "main", 2),
    ]

    clusters = build_ci_failure_clusters(observations, minimum_failures=3)

    assert len(clusters) == 1
    assert clusters[0].workflow_name == "Backend CI"
    assert len(clusters[0].observations) == 3
    assert clusters[0].branches == frozenset({"main", "release"})


def test_ci_failure_cluster_ignores_non_failure_or_unparseable_observations() -> None:
    asset_id = uuid4()
    observations = [
        SimpleNamespace(asset_id=asset_id, summary="Workflow Backend CI finished with success on main"),
        SimpleNamespace(asset_id=asset_id, summary="CI failed but summary has no canonical shape"),
        SimpleNamespace(asset_id=None, summary="Workflow Backend CI finished with failure on main"),
    ]

    assert build_ci_failure_clusters(observations) == []


def test_ci_failure_cluster_requires_three_failures() -> None:
    asset_id = uuid4()
    observations = [make_observation(asset_id, "Backend CI", "main", index) for index in (1, 2)]

    assert build_ci_failure_clusters(observations) == []


def test_ci_failure_cluster_applies_the_rolling_window() -> None:
    asset_id = uuid4()
    now = datetime.now(UTC)
    observations = [
        make_observation(asset_id, "Backend CI", "main", 1),
        make_observation(asset_id, "Backend CI", "main", 2),
        make_observation(asset_id, "Backend CI", "main", 3),
        SimpleNamespace(
            id=uuid4(),
            asset_id=asset_id,
            occurred_at=now - timedelta(days=8),
            summary="Workflow Backend CI finished with failure on main",
        ),
        SimpleNamespace(
            id=uuid4(),
            asset_id=asset_id,
            occurred_at=now + timedelta(minutes=1),
            summary="Workflow Backend CI finished with failure on main",
        ),
    ]

    clusters = build_ci_failure_clusters(
        observations,
        window_start=now - timedelta(days=7),
        window_end=now,
    )

    assert len(clusters) == 1
    assert len(clusters[0].observations) == 3


def test_ci_failure_severity_and_score_are_deterministic() -> None:
    assert ci_failure_severity(3) == "medium"
    assert ci_failure_severity(9) == "medium"
    assert ci_failure_severity(10) == "high"
    assert ci_failure_score(3) == 55.0
    assert ci_failure_score(10) == 90.0
    assert ci_failure_score(20) == 100.0


def test_fingerprint_and_evidence_ids_are_stable() -> None:
    asset_id = uuid4()
    opportunity_id = uuid4()
    observation_id = uuid4()

    assert _fingerprint(asset_id, "Backend CI") == _fingerprint(asset_id, "backend ci")
    assert _evidence_id(opportunity_id, observation_id) == _evidence_id(
        opportunity_id, observation_id
    )


def test_ci_failure_clusters_keep_repositories_and_workflows_separate() -> None:
    first_asset = uuid4()
    second_asset = uuid4()
    observations = [
        *(make_observation(first_asset, "Backend CI", "main", index) for index in (1, 2, 3)),
        *(make_observation(first_asset, "Frontend CI", "main", index) for index in (1, 2, 3)),
        *(make_observation(second_asset, "Backend CI", "main", index) for index in (1, 2, 3)),
    ]

    clusters = build_ci_failure_clusters(observations)

    assert {(cluster.asset_id, cluster.workflow_name) for cluster in clusters} == {
        (first_asset, "Backend CI"),
        (first_asset, "Frontend CI"),
        (second_asset, "Backend CI"),
    }
