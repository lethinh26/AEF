# 22 — Security, privacy và supply-chain: phân tích điểm phá vỡ

## 1. Trust boundaries

- B1: con người/admin UI → governance service (authenticated).
- B2: external sources → ingestion gateway (untrusted content).
- B3: World Model/retrieval → model context (data not instructions).
- B4: LLM output → Tool Gateway (must validate and authorize).
- B5: sandbox → host/network (least privilege isolation).
- B6: artifact → Git/CI/deployment (integrity and approvals).
- B7: project A → project B/capability registry (legal and tenant boundary).

Mỗi boundary có owner, authentication, authorization, auditing, rate limit, safe fallback, redaction.

## 2. Threat inventory

| Tình huống | Đường tấn công | Giảm thiểu |
|---|---|---|
| Prompt injection | README/log/PR chứa lệnh giả | taint-aware data handling; gateway permissions |
| Tool misuse | agent gọi shell xóa workspace/host | sandbox isolation, command profile, no host mounts |
| Exfiltration | payload chứa secrets gửi outbound | egress allowlist, secret scan, minimal context |
| SSRF | người dùng nhập base URL độc hại | admin only, DNS/IP validation, TLS, no redirects |
| Dependency compromise | install package/script độc | pin/SBOM, scanning, reproducible builds, approvals |
| Artifact tampering | PR/patch bị thay sau verify | commit SHA/digest, approval bound to diff |
| Cross-tenant leakage | memory returns other client snippets | ACL-first filtering, project partition, tests |
| Agent-to-agent spoofing | giả message “security approved” | signed service identities, no authority in message body |
| Resource exhaustion | tool loop/parallel swarm | quotas, concurrency, timeout, rate limits |
| Memory poisoning | false lesson promoted globally | provenance, independent eval, quarantine |

OWASP nêu các rủi ro excessive agency và prompt injection trong hệ thống LLM/agent [R6], và MCP cũng có hướng dẫn riêng về SSRF/token/authorization [R7].

## 3. Sandbox hardening checklist

- Container không chạy privileged; drop Linux capabilities; no Docker socket.
- UID không root; seccomp/AppArmor hoặc cơ chế tương đương; read-only root FS.
- Mount repository snapshot read-only ban đầu; writable overlay cho branch workspace.
- Không mount SSH/Git credentials production; credential broker cấp token có TTL.
- Network deny-by-default; chỉ allow egress được phép cho dependency download nếu cần.
- CPU/memory/PID/disk quota; timeouts; kill orphaned processes.
- Artifact extraction qua trusted process, scan và hash trước publish.
- Với code có thể mang tính thù địch hoặc nhiều tenant: microVM/hardened sandbox để tăng isolation; cần đánh giá threat model thực tế.

## 4. Secret management

Secrets chỉ ở vault/secret manager; provider API key, Git token, cloud creds không xuất hiện trong prompts/logs. Credential broker tạo token per mission, per repo, expiry ngắn; rotate/revoke. Implement redaction cả logs, crash traces, artifact previews. Trên UI hiển thị masked values; `test connection` không trả raw secrets cho frontend.

## 5. Privacy và IP

Tích hợp catalog quyền: nguồn dữ liệu, chủ sở hữu, allowed purpose, retention, model egress, redistribution rights. Nếu AI học pattern từ code thuộc khách hàng, cần kiểm tra quyền trích xuất thành reusable capability. Không coi “AI đã tóm tắt” là không còn rủi ro tiết lộ IP; invariants/domain knowledge cũng có thể nhạy cảm.

## 6. Supply-chain evidence

Sử dụng signed commits khi phù hợp, SBOM, pinned dependencies, build provenance, artifact digest, CI worker identity và branch protection. Tham khảo [SLSA v1.2](https://slsa.dev/spec/v1.2/). SLSA track không thay semantic verification nhưng giúp biết artifact đến từ đâu.

## 7. Key security decisions

- Read-only connectors trước, write connectors sau.
- Protected branches chỉ qua PR + reviewer gate; tránh direct push.
- Production không nằm trong scope giai đoạn nghiên cứu.
- Auto remediation chỉ giới hạn với tác vụ reversible/low-risk.
- Incident response phải hỗ trợ freeze toàn hệ thống và quarantine nguồn độc hại.
- Có runbook khi credential leak, policy bypass, unintended PR/deploy.

## 8. Chỉ số cần đo

Policy bypass attempts, denied tool calls, secrets detected pre/post redaction, sandbox escapes (mục tiêu 0), cross-project leak rate (mục tiêu 0), credential lifetime, artifact integrity failures, approval reuse attempts, dependency vulnerability exposure, mean time to revoke.
