# 07 — Engineering World Model: bản đồ vận hành có tính thời gian và bằng chứng

## 1. World Model khác RAG và code index

RAG hỗ trợ truy xuất; World Model hỗ trợ **quyết định trong thế giới có thay đổi**. Câu trả lời phải được xây từ các claim có kiểu, nguồn, timestamp, phạm vi, độ tin cậy và tình trạng xác nhận. Retrieval là một trong các đường tiếp cận World Model, không phải toàn bộ mô hình.

## 2. Ontology v0 (thực thể)

`Organization`, `Team`, `Person`, `Repository`, `Branch`, `Commit`, `CodeSymbol`, `Package`, `Component`, `Service`, `API`, `Database`, `Table`, `Queue`, `Deployment`, `Environment`, `CIJob`, `Incident`, `Alert`, `SLI`, `Goal`, `Finding`, `Opportunity`, `Mission`, `Capability`, `Artifact`, `Policy`, `Document`.

Nhóm thành 4 tầng: **inventory** (cái gì tồn tại), **topology** (phụ thuộc), **behavior** (trạng thái runtime), **intent** (mục tiêu/quy tắc). Đừng ép toàn bộ code AST vào graph persistence; lưu reference tới code index/commit và tạo các edges giá trị cao.

## 3. Relation vocabulary

`owns`, `depends_on`, `calls`, `reads_from`, `writes_to`, `deploys`, `exposes`, `measured_by`, `affected_by`, `implements`, `violates`, `supports_goal`, `introduced_by`, `validated_by`, `supersedes`, `possibly_causes`.

Quan hệ có `direction`, `valid_from/to`, `source`, `confidence`, `verification_state`, `scope`, `access_label`. Phân biệt `CALLS` suy ra từ static analysis và `CALLS` được trace xác nhận. Khả năng tự suy diễn nhân quả phải nằm ở một lớp riêng, không tự biến thành FACT.

## 4. Bitemporal evidence

**Schema đề xuất:**

```sql
CREATE TABLE world_claims (
  claim_id UUID PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_json JSONB NOT NULL,
  value_type TEXT NOT NULL,
  source_kind TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  source_hash TEXT,
  observed_at TIMESTAMPTZ NOT NULL,
  valid_from TIMESTAMPTZ,
  valid_to TIMESTAMPTZ,
  verification_state TEXT NOT NULL,
  confidence NUMERIC(4,3),
  sensitivity TEXT NOT NULL,
  retracted_by UUID,
  schema_version INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX world_claim_by_subject ON world_claims(tenant_id, subject_id, predicate);
```

Ở production, bổ sung `ingested_at`, `event_time`, `policy_version`, constraints, partition theo tenant và retention; schema này chỉ là phác thảo, chưa migration production-ready.

## 5. Claim evidence chain

Một claim `checkout-api → depends_on → inventory-service` có thể có chứng cứ:

1. Static import từ commit `abc` (supporting evidence).
2. OpenTelemetry trace `trace_id=...` của khoảng 15 phút (runtime confirmation).
3. Kubernetes service config bản `deployment_rev` (operational evidence).

Khi nguồn bất đồng, không chọn bên “tự tin” hơn theo lời model; tạo `DisputedClaim` và điều tra. Claim có thể đồng thời đúng trên branch main và sai trên release branch; mọi truy vấn phải scope rõ environment + revision.

## 6. Freshness/decay

Không áp TTL cố định cho mọi thứ. Ví dụ: ownership có thể tính theo ngày/tuần; active deployment tính theo phút; architecture decisions có thể tồn tại hàng tháng nhưng phải liên kết với version. Freshness policy theo claim class, owner, criticality.

`effective_confidence ≈ source_quality × corroboration × freshness × applicability` chỉ là heuristic; không coi là calibrated probability. Với quyết định có tác động cao, yêu cầu hard evidence và/or human review, không chỉ confidence lớn.

## 7. Reconciliation

- Webhook/CI event có thể lặp, muộn, mất thứ tự; dùng idempotency + source cursor.
- Repository branch bị force-push: invalidate edges gắn commit không còn reachable; không xóa lịch sử.
- Service đổi tên: dùng `canonical ID` và alias versioning, không gộp tự động nếu ownership khác.
- Data thiếu: trả `UNKNOWN` và list các source đang thiếu; không suy ra không có quan hệ.
- Multi-source contradictions: lưu tất cả, nâng cảnh báo khi critical.
- Source removal: đánh dấu provenance revoked; capability dùng nguồn đó phải re-evaluate.

## 8. Query API

`GET /world/assets?scope=...`, `GET /world/claims?subject=...&at=...`, `POST /world/impact-analysis`, `GET /world/coverage`, `GET /world/conflicts`, `GET /world/evidence/{id}`.

Mọi truy vấn AI phải lọc `tenant, user_access, purpose, sensitivity`, trả bằng chứng gốc cùng timestamp. Truy vấn “dịch vụ nào phụ thuộc checkout” cần trả `confirmed`, `inferred`, `unknown` riêng. Không dùng một đoạn văn không thể xác minh làm nguồn chân lý.

## 9. Metrics

- Asset coverage = confirmed assets / expected inventory (giới hạn theo nguồn đầu vào).
- Relation precision trên mẫu manual review; relation recall trên benchmark curated.
- Mean staleness và % claim phục vụ decision còn fresh.
- Contradiction resolution time; uncertainty-aware refusal rate.
- Impact analysis top-k precision; cross-project leakage count (mục tiêu 0).

## 10. Failure scenarios

**False dependency** khiến AEO đề xuất sửa service không liên quan; phải yêu cầu evidence cho impact paths. **Hidden dependencies** làm thiếu test; cần risk disclosure và post-change monitoring. **Schema changes** làm parser hỏng lặng lẽ; dùng source contract tests. **Prompt injection từ README**: tài liệu chỉ là data; không thể đưa thêm goal hay tool quyền.

Xem [Backstage Software Catalog](https://backstage.io/docs/features/software-catalog/) để tham khảo asset catalog/relations và [OpenTelemetry](https://opentelemetry.io/docs/concepts/signals/) cho signals; thiết kế world model/epistemic state ở trên là **[DESIGN]** của AEO.
