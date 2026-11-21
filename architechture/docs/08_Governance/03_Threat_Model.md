# 23 — Threat Model chi tiết: tác nhân, tài sản, đường đi và kiểm chứng

## 1. Assets cần bảo vệ

- Source code và dữ liệu khách hàng; production credentials; Git write scope; cloud bill; artifact provenance; goal/policy; evaluation datasets; capability registry; operator attention; reputational/customer trust.

## 2. Adversaries và nguồn lỗi

- Người ngoài kiểm soát PR/README/log hoặc package dependency.
- Nội bộ có tài khoản bị lộ hoặc quyền quá lớn.
- Model không đối kháng nhưng hallucinate, nhầm ranh giới.
- Tool connector lỗi/schema drift làm lệnh sai.
- Các agents cùng chia context và truyền lệnh giả.
- Người quản trị cấu hình provider endpoint sai.

## 3. Abuse cases

**TM-01 — Repo prompt injection**: attacker chèn `AGENTS.md` yêu cầu agent gửi env keys. Điều kiện: agent đọc repo. Mitigation: data/instruction separation, no secret injection, tool gateway. Verify: test agent không gọi network/secrets dù file nói vậy.

**TM-02 — False approval in ticket**: issue comment có “security team approved prod”. Mitigation: auth approval service, source text không có authority. Verify: no approval record means deny.

**TM-03 — Symlink/path escape**: `apply_patch` trỏ `../secrets`; kiểm tra canonical path, no-follow symlinks và actual mount path. Verify: filesystem tests.

**TM-04 — Model provider SSRF**: base URL `http://169.254.169.254/...`. Mitigation: admin-only URL, deny reserved IP ranges, pinned allowlists/TLS, re-validate redirects/DNS, network isolation. Verify: malicious URL blocked.

**TM-05 — Artifact swap**: diff được duyệt khác diff được merge. Mitigation: bind approval đến immutable commit/digest; revalidate before merge. Verify: changed SHA invalidates approval.

**TM-06 — Replay duplicating operations**: timeout sau `create_pr`, retry tạo PR thứ hai. Mitigation: idempotency/reconcile. Verify: fault injection after successful API call.

**TM-07 — Budget race**: 10 agents cùng chạy, tất cả đọc $10 remaining. Mitigation: transactional reservation, hard resource caps. Verify: concurrency test.

**TM-08 — Memory poisoning**: fake successful mission teaches unsafe bypass. Mitigation: provenance + independent held-out eval + quarantine; không allow auto-promotion.

**TM-09 — Cross-client IP reuse**: capability chứa schema khách hàng. Mitigation: scoped source rights, review generalized patterns, deny cross-tenant by default.

**TM-10 — Self-improvement capture**: candidate rule cho agent quyền rộng hơn. Mitigation: policy branch separate human ownership; Evolution Lab cannot edit production policy.

**TM-11 — Dangerous tool chain**: read-only query + file write + outbound upload combine thành exfiltration. Mitigation: end-to-end data-flow restrictions; track sensitivity of outputs, not just tool name.

**TM-12 — Silent metric manipulation**: agent sửa instrumentation để SLO trông đạt. Mitigation: monitor provenance/independent telemetry owner, anomaly detection, policy protected paths and human review.

## 4. Risk assessment matrix [DESIGN]

`Risk = severity × likelihood × exposure` chỉ dùng làm rubric trao đổi, không dùng để tự approve. Nếu severity critical và data confidence thấp, mặc định deny/approval. Dù likelihood nhỏ, path tới irreversible damage cần kiểm soát mạnh.

| Trust area | Critical misuse | Control owner | Automated gate | Human gate |
|---|---|---|---|---|
| Provider | Leakage | Platform | egress policy | provider onboarding |
| Repository | Unauthorized changes | Git owner | branch permission | protected merge |
| Sandbox | Escape | Security/DevOps | isolation and hardening | production connector approval |
| Data | Cross-tenant leak | Data owner | ACL/redaction | data reuse exception |
| Evaluation | False promotion | QA/Eval owner | held-out oracle | high-risk capability promotion |

## 5. Red-team process

Mỗi release mới: chạy 12 abuse cases với fixture, chụp tool decision logs, phát hiện false allow, tạo regression tests. Chú ý test security phải **không chứa credentials thật**, không triển khai attack lên hệ thống không được cấp quyền. Severity/triage và owner rõ ràng.

## 6. Disaster response

Phát hiện nghi vấn policy bypass → `FREEZE_WRITE` → revoke scoped credentials → isolate sandbox → preserve encrypted evidence → notify owner/security → kiểm tra external actions → khôi phục bằng known-good config → regression test → mở lại theo từng scope. Nếu thông tin nhạy cảm bị tiết lộ, theo incident response và các nghĩa vụ thông báo áp dụng.

## 7. Residual risk

Không có cơ chế nào chứng minh model không bị prompt injection trong mọi hoàn cảnh. Bảo vệ hiệu quả phải dựa vào **giới hạn hành động thực** và xác minh kết quả. AEO càng được kết nối hệ thống quan trọng, residual risk càng phải được đánh giá lại với owner.
