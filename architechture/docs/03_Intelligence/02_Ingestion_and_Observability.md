# 08 — Ingestion Plane: pipeline nguồn, chất lượng tín hiệu, privacy

## 1. Tập nguồn và quyền

| Nguồn | Dữ liệu | Trạng thái V0 | Rủi ro |
|---|---|---|---|
| GitHub/GitLab | repos, diffs, commits, PRs | Read-only | Token quá quyền, nội dung độc |
| CI/CD | run status, failed steps, test reports | Read-only | Logs chứa secrets |
| Dependency manifests | package + versions | Static scanner | False positive/vuln context |
| Issue tracker | ticket, labels, owner | Read-only | Personal data, source không tin cậy |
| OpenTelemetry | metrics, traces, log metadata | Synthetic/test hoặc read-only | PII, high volume |
| Cloud/K8s | deployments, incidents, cost | Sau V0 | Rủi ro production IAM |
| Docs/Figma/BRD | intents, specs | Theo quyền riêng | Embedding leakage, stale specs |

## 2. Ingestion lifecycle

`Register source → Authenticate minimal scope → Inventory snapshot → Read event → Validate schema → Redact → Deduplicate → Normalize → Attach provenance → Store immutable observation → Update materialized view → Trigger analysis`.

Chỉ bước `Update materialized view` thay đổi World Model current. Raw observation là audit input bất biến (tuân thủ retention và quyền xóa dữ liệu). Với PII, “immutable” không có nghĩa lưu vĩnh viễn: thiết kế khả năng xóa/crypto-shred theo chính sách hợp lệ, audit giữ metadata không nhạy cảm.

## 3. Event envelope

```json
{
  "event_id": "evt-01",
  "event_type": "ci.run.failed",
  "schema_version": 1,
  "tenant_id": "internal",
  "asset_id": "repo-checkout",
  "source": "gitlab-ci",
  "source_event_id": "pipeline-381",
  "event_time": "2026-11-21T03:00:00Z",
  "ingested_at": "2026-11-21T03:00:03Z",
  "correlation_id": "build-381",
  "sensitivity": "internal",
  "payload_ref": "artifact://events/evt-01.json",
  "payload_sha256": "<digest>"
}
```

Quy tắc: mỗi nguồn cung cấp `(source, source_event_id)` có thể dùng dedup; nếu thiếu thì tự tạo hash canonical fields và ghi chính sách approximation. Lưu `occurred_at` riêng với `received_at`.

## 4. Ingestion guarantees

Đừng hứa exactly-once từ webhook đến side-effects. Dùng **at-least-once + idempotent processing**, outbox/inbox, cursor checkpoints và reconciliation. Backfill phải có `snapshot watermark`, phân biệt event replay với thay đổi mới; không tạo hàng chục cơ hội giống nhau sau backfill.

## 5. Chất lượng dữ liệu

Theo dõi: availability của source, lag p50/p95, event loss estimate, duplicate rate, parse fail %, redaction coverage, schema drift, missing inventory, false attribution. Nếu nguồn critical bị mất hoặc metric quá cũ, downgrade Goal theo policy; không tự hành động ghi dựa trên dữ liệu suy đoán.

## 6. Sensitivity and data minimization

- Mask secrets qua nhiều bước: source connector, central redaction, log sink.
- Context LLM chỉ gửi trường cần thiết; ưu tiên test failure summary thay vì full raw logs.
- Bỏ tài khoản, email, token, key, payment data khỏi prompts; định danh cần thiết bằng pseudonym.
- Data retention theo tenant/purpose; quá hạn phải xóa bản gốc và index liên quan.
- Model provider policy về nơi lưu và dùng dữ liệu là **điều kiện hợp đồng** cần kiểm tra, không suy đoán từ chuẩn API.

## 7. Các tín hiệu chủ động hữu ích

- CI flakiness: cùng commit, nhiều lần chạy khác kết quả; không mặc định lỗi code.
- Test suite drift: test bị skip hoặc xóa tăng bất thường.
- Recurrent incidents: pattern lỗi lặp kèm impact.
- Dependency exposure: dependency mới gặp advisory đã xác minh applicability.
- Runaway cost: cloud bill hoặc agent compute vượt forecast.
- PR stagnation: review deadlock, quá nhiều merge conflicts.
- Knowledge gaps: service critical không owner, không SLO hoặc không runbook.
- Fault propagation: nhiều services có error cùng time window, cần correlation.

## 8. Độ sâu xử lý alert

`Raw Events → Group (fingerprints/time) → Incident Cluster → Hypothesis Set → Evidence collection → Findings → Opportunities`. Thiếu bước clustering thì một sự cố có thể thành 500 missions. Khóa dedup dùng `fingerprint + affected_assets + time_bucket + root_cause_cluster`, có người đánh dấu false positive và cơ chế reopen.

## 9. Shadow mode

Shadow mode vẫn có thể dùng API đọc dữ liệu, nhưng **không được tự mở branch/commit**. Kết quả xuất danh sách opportunities với lý do, chi phí dự kiến và mức độ uncertainty. Reviewer chấm blind sample: đáng làm/không đáng làm/cần dữ liệu; ghi adjudication để cải tiến detection.

## 10. Failure drills

- Mất webhook 6 giờ → resync từ cursor và tạo một finding thay vì bão events.
- Clock skew 20 phút → timeline không tự kết luận thứ tự nhân quả.
- CI log có malicious prompt → tool không được cấp thêm quyền.
- Dữ liệu repo đã đổi license/owner → index và transfer capability bị chặn.
- Redactor bỏ sót test secret → block outbound model call và mở incident nội bộ.
