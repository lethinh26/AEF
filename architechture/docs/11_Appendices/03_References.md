# 35 — Nguồn đối chiếu kỹ thuật (kiểm tra tới 2026-11-21)

> Tài liệu AEO là **đề xuất thiết kế và chương trình nghiên cứu**, không phải chuẩn quốc tế đang tồn tại dưới tên này. Các nguồn sau hỗ trợ những bộ phận kỹ thuật nền tảng; chúng **không chứng minh toàn bộ kiến trúc AEO là khả thi hoặc đã vượt coding agents hiện có**. Nội dung website có thể thay đổi sau thời điểm tham khảo.

| ID | Nguồn chính | Phạm vi liên quan |
|---|---|---|
| R1 | [Google SRE Workbook — Error Budget Policy](https://sre.google/workbook/error-budget-policy/) | SLO/error budget, trade-off reliability và innovation |
| R2 | [OpenTelemetry — Signals](https://opentelemetry.io/docs/concepts/signals/) | Metrics, traces, logs và telemetry model |
| R3 | [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/) | Inventory, entity relations, ownership model |
| R4 | [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs) | Policy as code, externalized authorization decisions |
| R5 | [Temporal — Workflow Execution](https://docs.temporal.io/workflow-execution) | Durable workflow execution, event histories, retries |
| R6 | [OWASP — Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | Rủi ro cấp quyền và tool misuse trong LLM apps |
| R7 | [MCP — Security Best Practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) | SSRF, token/authorization, trusted tool boundary |
| R8 | [SLSA v1.2 — Provenance](https://slsa.dev/spec/v1.2/provenance) | Integrity và nguồn gốc artifact/build |
| R9 | [NIST AI RMF](https://airc.nist.gov/airmf-resources/airmf/) | Govern, Map, Measure, Manage AI risks |
| R10 | [DORA — Software Delivery Metrics](https://dora.dev/guides/dora-metrics/) | Metrics về throughput và stability của delivery |
| R11 | [OpenAI — Function Calling](https://developers.openai.com/api/docs/guides/function-calling) | Tool calling cho native agent loop |
| R12 | [MCP Specification — Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | Tool schemas, semantics và trust warnings |
| R13 | [NIST AI RMF Playbook](https://airc.nist.gov/airmf-resources/playbook/) | Gợi ý vận hành quản trị/risk/evaluation |
| R14 | [SLSA v1.2 — Build Provenance](https://slsa.dev/spec/v1.2/build-provenance) | Artifact metadata và attestation requirements |
| R15 | [DORA — Value Stream Management](https://dora.dev/guides/value-stream-management/) | Value stream, bottlenecks và delivery performance |

## Phân biệt nguồn và suy luận

- SLO/error budget của SRE là [KNOWN]; Goal OS thích ứng chúng cho AI operations là [DESIGN].
- Backstage có catalog [KNOWN]; typed temporal evidence world model là [DESIGN].
- Temporal có durable execution [KNOWN]; chọn Postgres ở V0 là [DESIGN].
- OWASP ghi nhận các rủi ro agent [KNOWN]; AEO warrant/permit/gradation là [DESIGN].
- SLSA provenance là [KNOWN]; dùng provenance để suy ra software behavior là **không hợp lệ**.
- DORA metrics là [KNOWN]; AEO ROI/human attention là metrics **bổ sung**, không thay DORA.
- Function calling là capability API [KNOWN]; “mọi OpenAI-compatible endpoint đều hỗ trợ” là **sai/không được đảm bảo**.

## Quy trình cập nhật nguồn

Trước implementation, xác nhận version cụ thể của SDK, auth/transport/tool calling và số liệu benchmark. Ghi version pin trong ADR. Không dựa bài viết quảng cáo/vendor demo làm bằng chứng hệ thống sẽ vượt coding agents.
