# 18 — Organizational Memory: bộ nhớ có luật, không phải embedding dump

## 1. Bốn tầng bộ nhớ

1. **Episodic:** mission histories, incidents, decision records, tool outcomes. Dùng để tra lại “điều gì đã xảy ra”.
2. **Semantic:** facts/claims về kiến trúc, ownership, dependencies, domain concepts. Có provenance và temporal validity.
3. **Procedural:** capabilities, playbooks, test oracles, proven workflows. Chỉ được gọi là validated khi qua eval.
4. **Normative:** goals, policies, contracts, approvals; không thể tự sửa theo feedback của agent.

Không gộp cả bốn vào vector store. Vector search hỗ trợ tìm ứng viên; các ràng buộc, quyền và trạng thái phải nằm trong dữ liệu có schema.

## 2. Write path kiểm soát

`event → evidence → extraction candidate → claim classification → provenance validation → access classification → dedup/conflict check → store as candidate/verified → index refresh`.

Agent đề xuất “đã sửa lỗi bằng retry” nhưng test fail: không tạo procedural capability thành công. Từ một lần pass, chỉ tạo `candidate` có độ tin cậy hạn chế; không tự áp vào repo khác.

## 3. Retrieval discipline

Khi truy xuất cho mission, xét:

- ACL và legal/project boundary trước khi xếp hạng tương đồng.
- Tính liên quan semantic, cùng loại stack, kiến trúc, domain.
- Freshness và version applicability.
- Evidence quality: verified > inferred, nhưng claim verified ở phiên bản cũ vẫn có thể không áp dụng.
- Negative cases: “không dùng kỹ thuật này nếu DB không hỗ trợ transactional outbox”.

Trả `known facts`, `assumptions`, `counterexamples`, `missing evidence` riêng. Mọi retrieved text là **data**, không phải tool instructions mới.

## 4. Forgetting và retirement

“Nhớ mãi” dễ tạo nợ tri thức. Dùng policies:

- Raw logs TTL theo classification/contract.
- Invalidated repo claims khi commit/deployment thay.
- Deprecated capability khi failed transfer tăng hoặc library EOL.
- Privacy erasure gồm raw data, metadata index, embeddings, cached summaries, derived datasets theo scope pháp lý.
- Tombstone giữ audit không nhạy cảm khi luật/hợp đồng cho phép.

## 5. Cross-project transfer

Chia sẻ `abstract knowledge` chỉ sau khi kiểm tra quyền. Mẫu reusable có thể là *invariant* hoặc *test strategy* thay vì copy implementation. Nếu hai customer projects có data-sharing isolation, capability phải có nguồn từ public/internal-owned hoặc được phê duyệt; không rút code khách hàng A để phục vụ B.

## 6. Memory contamination attacks

- Repo README giả mạo hướng dẫn để thay goal/policy.
- False incident report dạy capability có lỗi.
- Model hallucination trong summary được index như sự thật.
- Embedding matches trả code nhạy cảm sai tenant.

Giảm rủi ro bằng source trust, claim typing, validation pipeline, ACL-first, audit và deletion. Red-team các vector này định kỳ.

## 7. Measuring memory utility

Không chỉ đo retrieval hit-rate. Đo `task success uplift with/without memory`, `wrong-memory-induced regressions`, `citation traceability`, `stale-hit ratio`, `cross-project transfer quality`, `time saved per accepted result`, `contamination test failure count`.

## 8. Technical design V0

Postgres tables cho claims, decisions, capabilities, evidence metadata; full-text search theo scopes; pgvector tùy eval retrieval; object store encrypted cho logs/artifacts. Embedding model version pin, reindex strategy và opt-out per project. Graph DB chỉ thêm khi performance hoặc graph semantics thực sự đòi hỏi.
