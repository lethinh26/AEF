# 17 — Verification & Evidence: độc lập, xác minh được, phân biệt outcome

## 1. Bốn tầng bằng chứng

- **L0 Procedural:** tool chạy được, không vi phạm quyền, artifact tồn tại đúng digest.
- **L1 Functional:** build/lint/unit/contract/E2E vượt oracle đã định.
- **L2 Operational:** staging/load/security checks, dependency và environment tương ứng.
- **L3 Outcome:** các chỉ số sau triển khai có bằng chứng cải thiện hoặc đạt ngưỡng qua cửa sổ đủ dài.

Không suy từ L1 ra L3. Việc một test pass không chứng minh tốc độ khách hàng cải thiện.

## 2. Độc lập nghĩa là gì?

Executor có thể tạo test đề xuất, nhưng acceptance tests nên gồm **hidden/held-out cases**, deterministic checks và review do bộ phận khác/CI của owner thiết lập. Model verifier có thể bổ sung review ngôn ngữ tự nhiên nhưng không thay test runner/policy. Không dùng một LLM vừa viết patch vừa tự đặt thang điểm và tự tuyên bố đạt.

## 3. Evidence schema

```json
{
  "evidence_id":"ev_789",
  "mission_id":"m_42",
  "kind":"verification.test_run",
  "source":"ci:test-checkout",
  "produced_at":"2026-11-21T06:00:00Z",
  "input_digest":"sha256:...",
  "artifact_digest":"sha256:...",
  "verifier_version":"test-runner@1.4",
  "environment":"sandbox-ci",
  "result":"PASS",
  "limitations":["Performance chưa benchmark"],
  "trust_tier":"L1"
}
```

Các digest được tính trên artifact thật, không phải chuỗi do model tạo. Evidence có thể có signature/attestation; phân biệt signed metadata với việc chứng minh nội dung là đúng.

## 4. Verification matrix

| Risk | Mức kiểm chứng tối thiểu | Điều kiện delivery |
|---|---|---|
| Branch docs/test | L0+L1 | PR creation |
| Feature normal | L0+L1+review | PR, staging khi policy cho phép |
| Payment/data logic | L0+L1+L2 + owner/security | human approval production |
| Infra production | L0+L1+L2 + approval | controlled rollout |
| Destructive operation | exception review + specific backup/rollback | deny by default |

## 5. Test integrity

- Test command từ repo phải chạy sandbox, không nhận `CI=true` do agent tự truyền để skip.
- Agent không được chỉnh acceptance oracle hidden.
- Test runner parse đúng số test chạy/skip/xfail; build status xanh nhưng `0 tests` không tự pass.
- Baseline test trước thay đổi để biết có lỗi sẵn.
- Flaky test phải chạy có kiểm soát, phân loại không pass giả bằng reruns vô hạn.
- Mutation testing/property-based testing có thể tăng độ tin cậy ở miền phù hợp, nhưng chi phí phải cân đối.

## 6. Outcome causal inference

Một cải thiện sau deploy có thể do traffic thấp, feature flag, cache nóng. Để kết luận hiệu quả, dùng một hoặc kết hợp: canary/control cohort, pre/post với kiểm soát seasonality, difference-in-differences nếu phù hợp, A/B khi có quyền và đủ traffic. Nếu không thể phân biệt nguyên nhân, ghi `OUTCOME_INCONCLUSIVE`.

## 7. Evidence Ledger không thể tự sửa

Sử dụng append-only event records, hash-linked digests hoặc object versioning cho audit; role tách biệt người sinh artifact và verifier. Dữ liệu nhạy cảm vẫn cần quy trình xóa theo luật/hợp đồng. Quyền truy cập evidence gắn scope tenant/project.

## 8. Promotion gates

- Build/acceptance pass.
- Không có critical unresolved findings.
- Diff reviewed hoặc có explicit policy tier tự merge.
- Reviewer nhìn được tác động, provenance và rollback plan.
- Mission không vượt budget/permissions.
- Post-deploy monitors được cấu hình trước rollout.

## 9. Nếu không có test oracle?

Không bắt AI “phán” rằng code đúng. Chọn `NEEDS_ACCEPTANCE_TEST`, tạo sample test proposals, thực hiện shadow review; nếu risk thấp có thể chuẩn bị patch nhưng không auto-complete. Đối với ứng dụng mới, yêu cầu domain acceptance do owner cung cấp hoặc phê duyệt.

## 10. Trường hợp phá hoại tinh vi

- Agent vô tình xóa test failing và tạo pass giả.
- Model reviewer thiên vị artifact do model cùng nhà sản xuất tạo.
- Unit test trôi xa thực tế production.
- Benchmark chọn workload thiên lệch.
- Evidence link đến artifact đã bị thay.
- CI credentials bị lộ trong log. Tất cả phải có test case trong acceptance suite.

Tham khảo [SLSA provenance](https://slsa.dev/spec/v1.2/provenance) về nguồn gốc artifact; **provenance không đồng nghĩa với semantic correctness**.
