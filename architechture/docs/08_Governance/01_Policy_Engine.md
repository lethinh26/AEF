# 21 — Policy Engine: quyết định quyền ở hành động, không dựa vào prompt

## 1. Mục tiêu

Thiết lập một **policy decision point (PDP)** độc lập và **policy enforcement points (PEP)** tại API, tool gateway, sandbox manager, Git connector, deployment connector. Bất kỳ lệnh agent nào có side-effect phải có permit do gateway xác nhận tại thời điểm thi hành.

## 2. Mô hình xác thực/xác quyền

Principal types: `human_user`, `service_worker`, `agent_run`, `connector`. LLM không phải identity principal có toàn quyền. Mission worker dùng short-lived identity, tool gateway mint scoped permit theo `mission_warrant + action_args + asset_acl + current_policy_version`.

RBAC cho vai trò tĩnh (operator/admin/reviewer), ABAC cho điều kiện (repo/env/tenant/risk/time/budget), relationship-based access cho owner và team. Không cần tự viết cả hệ identity nếu có IAM/OIDC hiện hữu.

## 3. Policy input

```json
{
  "principal":{"type":"agent_run","id":"run_117","tenant":"internal"},
  "mission":{"id":"m_42","goal_id":"goal_checkout_reliability","warrant_version":3},
  "action":{"tool":"git.create_pr","resource":"repo/shop-api","target_branch":"main"},
  "context":{"risk":"R1","policy_version":9,"diff_digest":"sha256:...","budget_remaining":4.5},
  "environment":{"mode":"sandbox","data_sensitivity":"internal"}
}
```

**Response:** `ALLOW`, `DENY`, `REQUIRE_APPROVAL`, `REQUIRE_EVIDENCE`, kèm `reason_code`, `constraints`, `expiry`, `decision_id`. Fail-closed khi policy không phản hồi và action có side-effect.

## 4. Policy evaluation order

1. Validate principal authentication + tenant scope.
2. Check charter status, owner revocation, active mission warrant.
3. Check action/tool capability, target assets, sensitive paths, sandbox health.
4. Check data classification/network/secrets restrictions.
5. Check budget + rate limit + concurrency + resource leases.
6. Check risk class, approval requirement, version/digest binding.
7. Mint permit ngắn hạn và log decision trước execution.
8. Observe result/side effect; reconcile và update quotas.

## 5. Approval & dual control

Human approval có thể cần hai người cho hoạt động trọng yếu; quy tắc tùy môi trường. Approval signed/recorded qua authenticated UI, **không chấp nhận lời nhắn trong repo như phê duyệt**. Khi diff/repo/target change, approval invalidation tự động. Không tự suy ra “approved” từ status message của LLM.

## 6. Sample policy logic

```text
allow if action == read_file
  AND repo in mission.scope
  AND mission.active
  AND principal.tenant == repo.tenant

auto_branch_write if action == apply_patch
  AND mission.permission == branch_only
  AND target_branch starts_with 'aeo/'
  AND path not in protected_paths
  AND budget_remaining > 0
  AND sandbox.attested

require_approval if action in {merge_protected, deploy_staging_with_data}

deny if action in {prod_delete_database, modify_iam_root, export_secrets}
```

Có thể dùng [Open Policy Agent](https://www.openpolicyagent.org/docs) khi cần policy-as-code phức tạp; không bắt buộc V0. Quan trọng hơn là enforce ở từng gateway.

## 7. Budget is authorization

Budget không phải dashboard. Với mỗi tool call reserve cost/steps/quota trước, reconcile actual sau. Nếu không đo được USD thật, quota “cost” phải được bổ sung bằng hard `requests/steps/time`. Không tăng quota theo đề nghị của agent. Khi hết quota, stop cleanly và escalate.

## 8. Data egress policy

Mỗi provider profile có `allowed_data_classes`, `regions`, `provider retention terms`, `embedding allowed`, `tool context restrictions`. Không gửi protected source code đến endpoint chưa được owner cho phép. Base URL do admin đặt phải chặn SSRF và redirect bất thường.

## 9. Revocation & audit

Revocation phải kill active sandbox credentials/tool permits; pending approvals invalidated; đang thực thi side-effect thì phải mark `CANCEL_REQUESTED` và compensation plan. Logs giữ `policy decision id`, principal, action digest, resource, outcome và reason. Giữ dữ liệu tối thiểu đủ audit; mã hóa và redact.

## 10. Bộ kiểm thử policy tối thiểu

- Path traversal, symlink escape, glob trick, git worktree symlink.
- Agent gọi tool không khai báo/args khác permit.
- Mission token dùng qua tenant khác.
- Approval dùng lại hoặc diff đổi sau approve.
- Budget race: 2 tool calls song song cùng tiêu hết quota.
- Provider config SSRF và egress.
- Policy service down: không cho write.
- Indirect prompt injection giả mạo quyền.
