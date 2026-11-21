# 03 — Những lựa chọn kiến trúc chưa chốt và ADR backlog

## 1. Phân biệt quyết định đã chốt với giả thuyết

**Đã chốt theo định hướng:** model thông qua OpenAI-compatible endpoint; nội bộ trước; bounded autonomy; goal-centric; evidence và quyền hành động do hệ thống ngoài LLM quản lý.

**Chưa chốt:** self-hosted vs cloud, graph DB hay relational graph, Temporal hay DB queue, một hay nhiều model, schema repository parser, mức tự chủ trên production, giá trị kinh tế mỗi Goal, danh mục nguồn dữ liệu đầu tiên.

## 2. ADR candidate matrix

| ADR | Phương án | Đề xuất V0 | Trigger xem lại |
|---|---|---|---|
| ADR-001 Workflow | Postgres job table / Temporal | DB state machine + outbox trước | Workflows nhiều ngày, compensate/replay phức tạp |
| ADR-002 World Graph | Postgres edges / Neo4j | Postgres typed entities & edges | Query multi-hop quy mô lớn trở thành bottleneck |
| ADR-003 Search | Full text / embeddings / hybrid | Full text + pgvector tùy nhu cầu | Recall thấp trên repo lớn |
| ADR-004 Agent engine | Native tool loop / vendor CLI | Native OpenAI-compatible adapter | Tool semantics không đủ/chi phí maintenance cao |
| ADR-005 Sandbox | Docker / gVisor / microVM | Docker cô lập trên host chuyên dụng, quyền thấp | Repo không tin cậy, tenant khác nhau, threat model cao |
| ADR-006 Product units | Single mission / swarm | Single agent trước, specialist theo yêu cầu | Benchmark chứng minh parallel advantage |
| ADR-007 Policy | Code rules / OPA | Rule engine typed, có thể thêm OPA | Cần policy đa tenant/triển khai phân tán |
| ADR-008 Evidence | DB only / object store | DB metadata + immutable objects | Artifact provenance phức tạp |
| ADR-009 Event bus | Outbox + worker / Kafka | Outbox + worker | Throughput và replay cần event streaming |
| ADR-010 UI | Portal first / API first | API + observability UI tối thiểu | Người vận hành khó đánh giá decisions |

## 3. Mẫu ADR được yêu cầu

```markdown
# ADR-XYZ: <tiêu đề>
Status: Proposed | Accepted | Superseded
Context: hiện trạng, lực ép, số liệu
Decision: phương án chọn, phạm vi, ngày
Alternatives: ít nhất 2 phương án và lý do bỏ qua
Consequences: lợi, hại, chi phí reversibility
Evidence: benchmark/thử nghiệm/nguồn
Risks & mitigations: rủi ro + owner
Review trigger: metric hoặc thời điểm rà soát
```

## 4. Câu hỏi phản biện trước khi code

1. AEO phục vụ **goals do ai sở hữu**? Product owner, SRE, khách hàng, tổ chức? Ai xử lý mâu thuẫn?
2. Hai repo có chủ sở hữu/điều khoản khác nhau thì nội dung nào được chia sẻ vào capability?
3. Chúng ta quan sát production ở dạng nào: chỉ số tổng hợp, logs đã redacted, hay dữ liệu chi tiết? Chính sách retention?
4. Số incident có đủ để đánh giá hiệu quả mission không? Làm sao phân biệt hồi quy với biến động tải?
5. Nếu model đổi, decision trace có còn giải thích được không?
6. Khi đạt SLO nhưng chi phí cloud tăng gấp đôi, goal optimizer xử lý ra sao?
7. Khi fail repair 3 lần, có rollback branch, quarantine capability và giảm cấp trust không?
8. Ai có quyền thu hồi mục tiêu, thu hồi credential, xóa bộ nhớ theo yêu cầu hợp đồng?
9. Với nguồn không có unit tests, oracle nào đáng tin để xác nhận hoàn thành?
10. Nếu CI xanh nhưng customer impact xấu đi, AEO có tự hạ confidence của capability không?
11. Có cách đo chi phí opportunity **không được chọn** để tránh thiên lệch survivorship không?
12. Đã có đối chứng với agent/task automation đơn giản chưa? Nếu không, chưa thể tuyên bố AEO vượt trội.

## 5. Quy tắc nghiên cứu

Mỗi đề xuất khác biệt phải được viết thành: `Problem → Hypothesis → Baseline → Intervention → Evidence → Risk → Decision`. Không được chuyển từ sơ đồ mô tả trực tiếp sang xây hệ thống lớn. Xem chương trình thí nghiệm ở khu 10.
