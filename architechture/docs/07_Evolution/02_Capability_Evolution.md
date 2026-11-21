# 19 — Capability Foundry: nhà máy chế tạo năng lực có bằng chứng

## 1. Capability là gì?

**Capability** = một năng lực sản xuất kỹ thuật tái sử dụng được, gồm **đầu vào/đầu ra, phương pháp, hành động được phép, phạm vi áp dụng, oracle đánh giá, provenance và hiệu quả đo được**. Không phải tên agent hoặc prompt đơn thuần.

Ví dụ `safe-idempotent-payment-retry` gồm: điều kiện gateway idempotency, retry policy, timeout/circuit breaker, data invariants, test harness concurrent requests, ví dụ cấu hình per stack, nguy cơ duplicate charge.

## 2. Capability manifest

```yaml
api_version: aeo/v1alpha1
kind: Capability
metadata:
  id: safe-retry-with-idempotency
  version: 0.2.0
  owner: platform-engineering
spec:
  purpose: 'Thiết kế và xác minh retry an toàn cho thao tác có side effect'
  prerequisites: ['idempotency_key_supported', 'reproducible_integration_tests']
  exclusions: ['non_idempotent_side_effect_without_compensation']
  applicability:
    domains: ['payments', 'order_processing']
    languages: ['python', 'typescript']
    environments: ['sandbox','staging']
  input_contract: 'schemas/retry_input.json'
  outputs: ['patch','tests','verification_report']
  process_ref: 'playbooks/retry_v2.md'
  verifier_ref: 'benchmarks/retry_safety_v1'
  required_permissions: ['repo_read','branch_write','sandbox_test']
  provenance: ['mission_110','eval_52']
  trust_tier: CANDIDATE
  license_policy: internal_only
```

Thực tế cần machine-readable typed schema, schema migration và explicit `model/tool compatibility`.

## 3. Capability lifecycle

`OBSERVED → EXTRACTED → CANDIDATE → LAB_EVALUATED → PILOT → VERIFIED → DEPRECATED / QUARANTINED / RETIRED`.

- `OBSERVED`: phát hiện pattern trong mission.
- `EXTRACTED`: tách điều kiện, hành vi, oracle, bất biến, chống chỉ định.
- `CANDIDATE`: có thể chạy trong Evolution Lab, chưa được general reuse.
- `LAB_EVALUATED`: có held-out case results với baseline.
- `PILOT`: dùng scope hẹp, canary.
- `VERIFIED`: đạt standard cho phạm vi cụ thể, không đồng nghĩa mọi stack.
- `QUARANTINED`: có incident/misbehavior, stop reuse ngay.
- `RETIRED`: không còn cần hoặc outdated.

## 4. Capability extraction algorithm

```text
collect successful + failed missions in a cluster
identify common invariant/process (LLM suggestion)
normalize input/output and prerequisites
extract negative cases and repair reasons
check IP/data rights before packaging
construct parameterized procedure + test oracle
search registry for duplicates/conflicting capabilities
create candidate with evidence links
schedule evaluation on tasks not used for extraction
```

Nếu không có oracle đáng tin hoặc missing rights, không promote. Có thể lưu “research note” không dùng để tự động hóa.

## 5. Versioning và compatibility

- SemVer theo interface: major cho breaking input/output, minor cho capability mới, patch cho sửa nội bộ.
- Pin version trong Mission Plan để replay/audit.
- `applicability envelope` phải được test: stack, framework versions, DB type, network architecture, regulatory domain.
- Thay đổi cap phiên bản mới không tự áp cho mission đang chạy.

## 6. Evaluation strategy

So sánh **AEO with capability** vs **AEO without** trên cùng benchmark held-out, randomize order, normalize model/version/budget and evaluation runner. Metrics `verified pass`, `time`, `cost`, `defect escape`, `human intervention`, `severity`. Phân nhóm theo stack. Ghi `negative transfer` khi reuse làm kết quả xấu đi.

## 7. Promotion rules [EXAMPLE]

- Tối thiểu 10 held-out cases đa dạng, không trùng training/extraction.
- Pass rate không thấp hơn baseline trong sai số thống kê hợp lý.
- Không vi phạm policy trong toàn bộ eval.
- Chi phí trung vị thấp hơn >15% **hoặc** accepted quality rõ ràng cao hơn.
- Human/security review với capability dữ liệu và thanh toán.

**Các ngưỡng này là giả định thí nghiệm, không phải chuẩn có sẵn**; cần điều chỉnh theo dữ liệu.

## 8. Khác model fine-tuning

Đa phần cải tiến ban đầu nên là procedure, tool router, retrieval, test harness và knowledge. Fine-tuning có thể hữu ích sau khi có dữ liệu được quyền dùng và eval sạch, nhưng không phải cốt lõi để tổ chức tự cải tiến.

## 9. Failure modes

- **Overfitting:** candidate chỉ tốt trên bài đã thấy.
- **Negative transfer:** giải pháp payment cho SaaS không phù hợp ecommerce traffic.
- **Capability bloat:** registry có hàng nghìn skill khó tìm; cần dedup/retirement.
- **Contaminated benchmark:** bài test bị dùng lúc extraction.
- **Security drift:** workflow mới bypass approval.
- **Ownership violation:** trích code proprietary thành template chung.

## 10. Thành công của Foundry

Không phải số capability tăng. Phải đo `coverage of high-value recurrent work`, `reuse activation rate`, `measured transfer uplift`, `maintenance cost`, `rollback rate`, `time to verified capability`. Một registry nhỏ có 20 capability tốt có thể tốt hơn 2.000 prompts vô kiểm chứng.
