# 25 — Canonical Data Model: thực thể, tính nhất quán, versioning

## 1. Danh mục bảng v0

```text
identity: organizations, users, teams, memberships, assets, asset_acl
planning: goals, goal_versions, goal_measurements, goal_conflicts
world: observations, claims, claim_evidence, world_snapshots, source_cursors
analysis: findings, hypotheses, opportunities, opportunity_evidence
portfolio: decision_records, allocations, resource_leases, budget_reservations
missions: missions, mission_versions, tasks, task_dependencies, runs, checkpoints
execution: tool_calls, tool_decisions, sandboxes, branch_changes
quality: verifications, evidence_records, outcome_observations
knowledge: capabilities, capability_versions, applicability, capability_evaluations
security: policies, policy_versions, approvals, revocations, security_incidents
infra: outbox_events, inbox_dedup, audit_events, artifact_metadata
```

`Organization` dù nội bộ vẫn cần để làm future multi-tenant, nhưng V0 có thể một tenant. Không dùng one giant `json` blob cho toàn bộ entities, nhưng dùng JSONB cho dynamic domain-specific schema với typed validation.

## 2. Entity cardinalities

- One `Goal` → many `GoalVersions`, `Opportunities`, `Missions`.
- One `Observation` → many `Claims/Findings`, có thể zero.
- One `Finding` → many `Opportunities`; Opportunity có thể kết hợp nhiều Findings.
- One `Decision` → many candidate refs + one chosen action, `supersedes` optional.
- One `Mission` → many `Task/Run/Evidence`, one current plan version.
- One `Capability` → many versions/evals; Mission pins version.
- One `Approval` → one scoped action + digest, single use.

## 3. PostgreSQL sample DDL

```sql
CREATE TABLE goals (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  owner_id UUID NOT NULL,
  current_version INTEGER NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, id)
);
CREATE TABLE goal_versions (
  goal_id UUID NOT NULL REFERENCES goals(id),
  version INTEGER NOT NULL,
  spec JSONB NOT NULL,
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(goal_id, version)
);
CREATE TABLE missions (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  goal_id UUID NOT NULL REFERENCES goals(id),
  opportunity_id UUID,
  decision_id UUID,
  state TEXT NOT NULL,
  current_plan_version INTEGER NOT NULL DEFAULT 1,
  base_commit_sha TEXT,
  policy_version INTEGER NOT NULL,
  row_version INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE outbox_events (
  id UUID PRIMARY KEY,
  aggregate_type TEXT NOT NULL,
  aggregate_id UUID NOT NULL,
  aggregate_version INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX outbox_aggregate_version
  ON outbox_events(aggregate_type, aggregate_id, aggregate_version);
```

DDL là mẫu chưa đầy đủ constraints, FK và RLS; khi làm thật cần migration, index, tenant-aware row-level authorization, backup/restore tests.

## 4. Consistency and concurrency

- Domain aggregate updates dùng transaction + optimistic lock `WHERE row_version = expected`.
- Outbox event được ghi cùng transaction state change.
- Consumer có inbox dedup `(consumer_id, event_id)`.
- Không giả định event đến đúng thứ tự; bảo vệ bằng aggregate version và snapshot reconciliation.
- Artifact content ở object store: write temp → hash/scan → publish metadata transaction; nếu thiếu object, verifier không PASS.
- Budget reservation dùng atomic SQL update/lock tránh double spending.

## 5. Event sourcing vs audit log

Không cần full event sourcing cho V0. Dùng canonical state + append-only audit/outbox. Khi dài hạn cần historical replay một số aggregate, có thể bắt đầu `Mission events` rõ định nghĩa. Tránh tạo 100 event types không có consumer/evidence.

## 6. Data retention

Phân loại `P0 secrets (never persist)`, `P1 restricted`, `P2 internal`, `P3 public`. Chính sách TTL theo loại dữ liệu, mục đích, consent và hợp đồng; phải xử lý cả derived artifacts/index, backups và deletion audit. Các immutable logs chỉ bất biến về sửa lịch sử trong cửa sổ lưu trữ hợp pháp, không mặc định vĩnh viễn.

## 7. Migration/version contracts

Version schema `api_version` cho public entities, `schema_version` cho event types. Field mới additive trước; field breaking cần adapter và migration. Consumer phải bỏ qua field unknown an toàn nhưng không âm thầm bỏ missing required. Mọi plan/evidence pin version để audit.
