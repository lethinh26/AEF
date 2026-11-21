# 12 — Mission Protocol: hợp đồng vận hành giữa ý định và tác động

## 1. Mission không phải prompt

Mission là **đơn vị trách nhiệm tạm thời**: có lý do tồn tại (opportunity/goal), output có thể kiểm chứng, quyền được cấp, chi phí, điều kiện hủy và cơ chế hậu kiểm. Một Goal có nhiều Missions. Mission có thể dài phút, giờ, ngày; agent sessions có thể được thay thế mà Mission vẫn tồn tại.

## 2. Mission Contract v0

```yaml
api_version: aeo/v1alpha1
kind: Mission
metadata:
  id: mission_checkout_ci_042
  tenant_id: internal
  goal_ref: goal_checkout_reliability@7
  opportunity_ref: opp_117@2
spec:
  type: bugfix
  objective: 'Sửa regression khiến test checkout flake trên branch main'
  target:
    repository: shop-checkout
    base_commit: 'abc1234'
    branch: 'aeo/mission_checkout_ci_042'
    environment: sandbox
  acceptance:
    - id: reproduce
      kind: test
      command_ref: test:checkout_failing_case
      required: true
    - id: regression
      kind: test
      command_ref: test:checkout_regression
      required: true
  constraints:
    protected_paths: ['config/production/**','infra/production/**']
    forbidden_actions: ['prod_deploy','merge_protected','delete_database']
    max_changed_files: 20
  resources:
    llm_provider_profile: primary
    budget_usd_estimate: 10 # EXAMPLE
    max_steps: 60
    max_elapsed_seconds: 3600
    max_repair_cycles: 2
  permissions:
    mode: branch_only
    can_read_repo: true
    can_write_sandbox: true
    can_create_pr: true
  outcome_measurement:
    metric_refs: ['checkout_ci_failure_rate']
    observation_window: 7d
  human_contact: oncall_team
status:
  state: PROPOSED
```

YAML chỉ định nghĩa contract; backend phải validate với typed schema và kiểm tra quyền từ identity principal/owner, không tin trường do LLM tạo là grant hợp lệ.

## 3. State machine chi tiết

```text
PROPOSED -> ELIGIBILITY_CHECK -> (REJECTED | NEEDS_EVIDENCE | APPROVED)
APPROVED -> RESERVING -> PLANNING -> (WAITING_INPUT | EXECUTING)
EXECUTING -> (VERIFYING | BLOCKED | CANCEL_REQUESTED | TIMED_OUT)
VERIFYING -> (REPAIRING | READY_TO_DELIVER | FAILED)
REPAIRING -> EXECUTING (bounded)
READY_TO_DELIVER -> (WAITING_APPROVAL | DELIVERING)
WAITING_APPROVAL -> (DELIVERING | REJECTED | EXPIRED)
DELIVERING -> (PENDING_OUTCOME | COMPLETED_WITHOUT_OUTCOME | FAILED_DELIVERY)
PENDING_OUTCOME -> (OUTCOME_VERIFIED | OUTCOME_INCONCLUSIVE | OUTCOME_NEGATIVE)
any eligible state -> CANCEL_REQUESTED -> COMPENSATING -> CANCELLED
```

`COMPLETED_WITHOUT_OUTCOME` nghĩa là đầu ra kỹ thuật xong, chưa chứng minh giá trị sau triển khai. Không được hiển thị như “Goal achieved”.

## 4. Preconditions, invariants, postconditions

**Preconditions:** owner hợp lệ, repo reachable, base commit tồn tại, policy snapshot hợp lệ, budget khả dụng, sandbox healthy, source data không quá stale. **Invariants:** không write ngoài workspace, không tăng quyền, mỗi side effect có idempotency, không vượt budget, không reuse credentials giữa tenants. **Postconditions:** diff/artifacts có digest, independent test evidence, record consumed budget, provenance, outcome schedule hoặc lý do không thể đo.

## 5. Mission DAG

Task nodes gồm: `id, role, objective, input_refs, output_contract, dependencies, permissions, timeout, max_attempts, verifier_ref`. Edges phải acyclic; plan validator kiểm tra critical path, side effects, overlapping file writes, barrier trước merge, resources. Replan tạo `plan_version`, không overwrite cũ; diff plan lưu reason và permission reassessment.

## 6. Mission Ledger và provenance

Mọi hành vi được ghi theo chuỗi:

`MissionCreated → EligibilityPassed → PlanProposed → PlanValidated → TaskStarted → ToolPermitted → ToolExecuted → ArtifactProduced → TestCompleted → VerificationCompleted → DeliveryRequested → ApprovalGranted → DeliveryCompleted → OutcomeObserved`.

Từng event gồm `actor`, `correlation_id`, `causation_id`, `policy_eval_id`, `input digest`, `output digest`, `sequence`, `timestamps`. Event ledger không phải toàn bộ raw prompt; có thể lưu encrypted trace với retention phù hợp, tránh lưu secrets.

## 7. Cancellation and partial completion

Nếu user hủy khi agent đang sửa file, dừng tool call mới; snapshot workspace; đánh dấu artifacts là partial. Nếu tạo PR thành công rồi API response timeout, **reconcile theo external id/idempotency key**, không tạo PR thứ hai. Nếu external side effect không có rollback, record `manual_recovery_required` và escalation.

## 8. Outcome follow-up

Mission có hai kết quả: `execution_result` và `outcome_result`. Ví dụ PR merged nhưng SLO không đổi; technical task completed nhưng outcome unverified. Vòng lặp sau không được tự tạo vô hạn ticket sửa cùng vấn đề; cooldown, new evidence threshold, human arbitration.

## 9. Mission type taxonomy

`INVESTIGATE`, `REPAIR`, `IMPLEMENT`, `REFACTOR`, `INTEGRATE`, `DATA_TRANSFORM`, `INFRA_CHANGE`, `VERIFY`, `DOCUMENT`, `CAPABILITY_EXPERIMENT`. Mỗi loại map capability và oracle khác nhau; không ép mọi loại vào pipeline `generate code → run unit tests`.
