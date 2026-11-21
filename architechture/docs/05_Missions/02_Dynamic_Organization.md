# 13 — Dynamic Engineering Organization: cấu hình tổ chức theo nhiệm vụ

## 1. Vì sao “nhiều agent” không đủ

Một sơ đồ CEO/PM/Architect/Dev/QA agents cứng dễ tạo token overhead và lỗi truyền miệng. AEO không có fixed headcount; nó **tạo execution topology** theo đòi hỏi thực tế của mission. Organization design là quyết định tài nguyên có thể đo, không phải vai diễn trong prompt.

## 2. Ba dạng topology

- **Sequential single-agent + independent verifier:** thích hợp bugfix nhỏ; ít coordination, context đơn giản.
- **Parallel independent tasks + integration barrier:** thích hợp dịch vụ tách được, test suites độc lập; phải có conflict prediction.
- **Specialist review / adversarial verification:** tác vụ rủi ro cần người/agent độc lập phân tích security, migration, correctness; không cần tất cả specialists viết code.

V0 mặc định một agent executor và deterministic verifier. Chỉ nâng topology khi benchmark chứng minh lợi ích sau coordination costs.

## 3. Organization Compiler

Input: Mission Contract, World Model snapshot, Capability Registry, resource availability, policy envelope. Output: `ExecutionTopology` gồm DAG, role capabilities, permitted tools, team boundaries, cost ceiling, join conditions, integration checkpoints.

```text
parse mission acceptance
-> classify work and blast radius
-> collect capabilities with applicability match
-> estimate task independence / shared files
-> select topology minimizing risk + coordination cost
-> allocate actor identities and scoped tool tokens
-> validate policy and DAG
-> publish plan version
```

**No magic staffing:** Nếu một capability không có executor phù hợp, trả `CAPABILITY_GAP`, không tạo agent tên đẹp với giả định model hiểu mọi thứ.

## 4. Artifact handshake

Agents không truyền “tôi đã sửa xong” dưới dạng chat tùy ý. Mỗi task output là artifact có contract:

```yaml
task_result:
  task_id: t-api
  state: READY_FOR_VERIFY
  base_commit: abc1234
  produced_commit: def5678
  files_changed: [src/api.py, tests/test_api.py]
  artifact_refs: [artifact://diff/t-api.patch]
  test_evidence: [evidence://ci/run_234]
  blockers: []
  unverified_claims: ['Load benchmark chưa chạy']
```

Verifier kiểm tra digest, base commit và test; integration agent không được mặc định đúng.

## 5. Communication discipline

- Giao tiếp qua message bus/typed events và artifact refs, không “chat room” vô hạn.
- Mỗi message có sender/recipient/mission id/type/sequence/time/budget.
- Không có lệnh agent-to-agent cấp quyền; mọi tool call vẫn qua policy gateway.
- Merge conflict sẽ tạo `INTEGRATION_CONFLICT`, không cho agents tự force-push vào main.

## 6. Topology example

Mission xây chức năng coupon cho e-commerce:

`Requirement contract` → `Domain spec` → song song `API implementation`, `Admin UI`, `Data migration design` (migration không tự áp production) → `Integration` → `E2E acceptance` → `Security review` → `Staging delivery`.

Cần xem rõ `coupon eligibility` là invariant chung; nếu domain spec mơ hồ, không để UI/API tự diễn giải khác nhau.

## 7. Chống hội chứng bầy đàn

- **Consensus illusion:** 3 model đồng ý chưa chắc đúng nếu cùng context sai. Sử dụng dữ liệu/test độc lập.
- **Coordination inflation:** nhiều thông điệp nhưng ít artifact.
- **Diff conflict:** các agents sửa chung code; dùng ownership per task, narrow branches và integration queue.
- **Specialist hallucination:** role label không tạo ra chuyên môn; benchmark capability mới là tiêu chí.
- **Runaway delegation:** mỗi agent đẻ agents mới; chỉ scheduler được cấp slot, số agent tối đa trong mission warrant.

## 8. Metrics và quy tắc nâng cấp topology

`accepted_outcomes/hour`, `cost/outcome`, `context transfer errors`, `merge-conflict rate`, `rework caused by integration`, `tool violations`. Nếu multi-agent không cải thiện đáng kể so với single-agent baseline trên workload held-out, giữ single-agent.
