# 14 — Long-horizon reliability: tồn tại qua giờ, ngày, restart và lỗi ngoài

## 1. Thực tế của agent workflows

Một mission có thể bị gián đoạn bởi mất API, worker crash, model không phản hồi, checkout branch đổi, PR đã được tạo mà callback thất bại, approval hết hạn. “Retry prompt” là không đủ: cần execution history + tool side-effect reconciliation.

## 2. Durable vs deterministic

Workflow state là deterministic, agent steps mang tính stochastic. Không đặt LLM call trực tiếp trong phần replay deterministic nếu workflow engine yêu cầu determinism; gọi qua activity/job với ID, lưu output và payload digests. Temporal hỗ trợ long-lived executions, histories và activities; V0 có thể dùng DB state machine nếu thao tác ít và chấp nhận giới hạn [R5].

## 3. Recovery record

```yaml
checkpoint:
  mission_id: m_42
  plan_version: 3
  task_id: t_patch
  step_id: 17
  repo_base: abc1234
  workspace_snapshot_digest: sha256:...
  artifacts_written: [artifact://...]
  tool_call_state:
    external_action_id: pr-291
    status: OBSERVED_SUCCESS
  remaining_budget:
    max_steps: 33
    max_elapsed_seconds: 1100
  policy_version: 9
```

State resume không đảm bảo LLM reasoning được tái tạo chính xác; cần context summary + tool results + checkpoint, kiểm chứng lại preconditions.

## 4. Failure classification

- **Transient provider:** 429/5xx; exponential backoff + jitter, cap.
- **Permanent provider:** auth/config/model capability unsupported; stop và escalate.
- **Tool failure:** JSON invalid, command exit nonzero; capture stderr/exit code; model có thể repair.
- **Environment failure:** sandbox OOM; diagnose resource class, không tự tăng quota vượt budget.
- **Policy failure:** deny; không retry bằng lệnh tương đương lách policy.
- **Verification failure:** test fail, coverage etc; bounded repair.
- **Unknown side-effect:** API timeout after create PR; query external by idempotency/ref trước khi retry.
- **Stale-world:** base commit changed, goal revoked; pause/replan với snapshot mới.

## 5. Idempotency layers

`command` có thể không idempotent (SQL UPDATE, script). Với operations có side effects, ưu tiên declarative desired-state + dry-run + approval + observed-state reconciliation. Git checkout/patch trong sandbox riêng có thể reset từ known commit. Creating PR/comment cần external key và dedup. Không coi shell arbitrary là an toàn khi retry.

## 6. Compensation & saga

Không phải mọi thứ reversible. Tạo branch có thể xóa; PR có thể close; deployment staging có thể rollback, nhưng migration destructive có thể không phục hồi. `Compensation` phải được thiết kế theo loại hành động, được cấp quyền và test trước; không tự suy diễn `reverse SQL`.

## 7. Timeout, liveness, deadlock

- Runtime heartbeat, lease expiry, watchdog dừng runaway.
- Step deadline và mission deadline riêng.
- Phát hiện DAG không tiến triển (blocked cycle), lock starvation, approval expiry.
- Model tool loop không được tiếp tục khi `max_steps`/`max_elapsed` hết.
- `pause` không xóa tài nguyên đang sở hữu mà chưa ghi checkpoint.

## 8. Degradation strategy

Khi model provider lỗi, hệ thống vẫn tiếp tục thu signals, cập nhật world model và xếp hàng opportunities nhưng **không tự đánh dấu đã xử lý**. Khi policy service lỗi, fail-closed với write actions; read-only queries có thể chạy theo profile được phép. Khi object store lỗi, không mark artifact verified.

## 9. Chaos testing

Bộ thử: kill worker trước/sau Git commit, drop provider mid-tool response, mất CI webhook, approval hết hạn giữa delivery, force push branch, duplicate event, lock bị orphan, revoked token, corrupt artifact digest. Tiêu chí: không double effect, không vượt quyền, recovery có evidence, operator thấy chính xác trạng thái.
