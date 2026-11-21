# 16 — Production System: sản xuất mới, sửa đổi, kết hợp và tái cấu hình

## 1. C không chỉ là tạo code từ prompt

Production Engine phải biết **chế tạo những artifact kỹ thuật theo contract** từ catalog năng lực có điều kiện áp dụng; có thể chọn tạo mới khi catalogue không khớp. Đối tượng sản xuất: patch, service, library, workflow, migration plan, CLI, web/mobile app, test harness, IaC, docs, runnable prototypes.

## 2. Các kiểu công việc có verification khác nhau

| Job kind | Output | Oracle đáng tin |
|---|---|---|
| Bugfix | regression patch | reproduce-before, pass-after, no new regressions |
| Feature | implementation + contracts | acceptance tests, UX/business review |
| Script | tool, transformed files | deterministic fixtures, checksum, safe sample |
| API integration | connector | contract tests, fake service, error handling |
| Data migration | migration plan/scripts | dry-run, data invariants, rollback proof, approval |
| Infra change | IaC | plan/diff, policy scan, staging evaluation |
| Security fix | mitigation PR | exploit regression test, independent review |
| Performance | benchmark patch | representative workload, controlled before/after |

Không một verifier duy nhất phù hợp mọi loại.

## 3. Intent-to-Contract Compiler

Trước code, tạo `Requirement Contract` gồm **functional requirements, nonfunctional constraints, invariants, open questions, dependencies, outcome expectations và approval needs**. Đầu vào có thể là BRD/Figma/ticket/ý tưởng. Những thứ cần người quyết định (giá/logic hoàn tiền/quyền truy cập/pháp lý) phải đi qua `NEEDS_CLARIFICATION`.

**Ví dụ coupon:**

- Không cho dùng coupon quá hạn; định nghĩa timezone.
- Một đơn hàng chỉ được trừ tiền trong giới hạn hợp lệ.
- Tổng chiết khấu không âm tổng tiền; quy tắc rounding rõ.
- Checkout concurrent không vượt usage limit.
- Refund/cancel định nghĩa rõ ảnh hưởng quota.
- Các behavior này được chuyển thành test vectors trước khi agent viết code.

## 4. Product Line Composition

Một capability có thể cung cấp `RBAC`, `Audit Log`, `Payments`, `Notification`, `Coupon Eligibility`; nhưng ghép không đơn giản như Lego. Cần `Capability interface`, semantic compatibility, data ownership, API version, latency/consistency requirements, security boundaries, license, deployment constraints.

**Composition algorithm đề xuất:**

1. Derive requirement constraints.
2. Retrieve candidates by semantic function **và** applicability metadata.
3. Solve compatibility constraints trước khi chọn.
4. Choose `reuse`, `adapt`, `rewrite`, `research` theo cost/risk.
5. Generate integration contract & tests.
6. Sandbox assembly + verification.
7. Emit provenance tới từng capability version và dependency.

## 5. “Reusable blueprint” gồm những gì?

- Domain invariants, threat assumptions, API contracts.
- Sample implementation variants (theo stack) nếu license cho phép.
- Test harness có positive/negative/edge cases.
- Adaptation instructions và chống chỉ định.
- Version, trust tier, provenance, evaluation score trên held-out cases.
- Known failure modes, regression warnings, retirement criteria.

## 6. Có nên sinh cả CRM hoặc thương mại điện tử từ một câu?

Có thể cho phép **giai đoạn discovery/prototype**, nhưng không cam kết production-ready nếu thiếu nghiệp vụ/acceptance/oracles. Phân thành `Product Intent → Domain Map → bounded slices → integration milestones → security/quality gates → pilot rollout`. Product generation phải duy trì thống nhất domain terms, data contracts và migration strategy trên các slice.

## 7. Supply-chain và dependency hygiene

- Pin dependencies/version; kiểm tra license, SBOM và advisories.
- Build artifacts gắn source commit, toolchain version, test evidence, build provenance.
- Không tự tải random scripts rồi chạy, ngay cả khi model đề xuất.
- Template/capability update phải có compatibility testing và rollback.

## 8. Quy tắc giảm technical debt

- Mỗi thay đổi có `owner`, `test impact`, `maintenance plan`.
- Không thêm abstraction chỉ để tăng code sophistication.
- Refactor không được tự tăng phạm vi nếu acceptance chỉ là bugfix.
- Theo dõi file churn, complexity proxies và defect escape; metrics có thể sai, cần sample human review.
- Chặn “fix bằng cách tắt test/lint” trừ approved intent cụ thể.

## 9. Output contract

Một delivery package tối thiểu có `branch/patch`, `architecture impacts`, `test evidence`, `known limitations`, `policy approval status`, `artifact checksums`, `rollback guidance`, `pending outcome monitors`. Không gọi artifact “production ready” nếu chưa qua production acceptance thực sự.
