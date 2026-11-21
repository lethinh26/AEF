# 15 — Native Agent Runtime: OpenAI-compatible, không phụ thuộc Codex

## 1. Hai ranh giới bất biến

1. **LLM reasoning adapter** chỉ nhận/gửi messages, tool schemas, usage, errors; không có quyền host shell/Git/secrets.
2. **Tool execution gateway** là nơi duy nhất có thể gây side effects, thực thi sau schema validation, policy decision, quota và sandbox dispatch.

Một endpoint “OpenAI-compatible” không đồng nghĩa hỗ trợ đầy đủ: tool calling, JSON schema, parallel tool calls, streaming, vision, token usage, response roles và input context có thể khác nhau. Phải có capability probe; không fallback sang parse text thành shell command khi endpoint không có tool semantics đáng tin cậy.

## 2. Provider profile

```yaml
provider:
  id: primary
  transport: openai_chat_completions
  base_url_secret_ref: secret://models/primary/base_url
  api_key_secret_ref: secret://models/primary/api_key
  model: configured-model
  timeout_seconds: 120
  request_retries: 2
  supported:
    tool_calls: probed
    parallel_tool_calls: false
    strict_json_schema: false
    streaming: false
  outbound_hosts_allowlist: ['model-provider.example']
```

Base URL admin-controlled; validate scheme HTTPS, DNS/IP SSRF, redirects, localhost/link-local/cloud metadata, TLS; nếu dùng local internal endpoint, phải có cấu hình trust riêng. Không cho agent chỉnh provider config bằng tool calls.

## 3. Tool calling loop (giả mã)

```python
async def run_task(task, warrant, context):
    limits = Limits(warrant)
    messages = build_context(task, context)
    while limits.allow_next_step():
        answer = await provider.complete(messages, allowed_tool_schemas(warrant))
        limits.consume_usage(answer.usage)  # may be estimated / bounded separately
        if answer.has_tool_calls:
            for call in answer.tool_calls:
                args = schema_validate(call.name, call.arguments)
                permit = policy.authorize(warrant, call.name, args)
                if not permit.allowed:
                    result = tool_error('POLICY_DENIED')
                else:
                    result = await sandbox_gateway.execute(call, args, permit)
                ledger.append_tool_result(call, result)
                messages = append_protocol_messages(messages, call, result)
            continue
        if answer.final:
            return TaskCandidate(answer.final, ledger.references())
    return TaskStopped(reason=limits.reason())
```

Pseudo-code có lược bỏ exception handling/parallel outputs/context; phải tuân đúng message protocol của provider và lưu records trước/sau mỗi side effect.

## 4. Tool Registry typed và sensitivity

| Tool | Inputs quan trọng | Quyền mẫu | Safeguard |
|---|---|---|---|
| `list_files` | path/glob | read repo | chặn path traversal |
| `read_file` | path/range | read repo | secret scanner, output cap |
| `search_code` | query/scope | read repo | timeout, allowlist |
| `apply_patch` | patch/base sha | write branch | preimage check, protected paths |
| `execute_command` | command profile, args | sandbox-only | no arbitrary host shell, resource limits |
| `run_tests` | approved command ref | sandbox | parse report + digest |
| `git_diff` | base/current | read sandbox | validate base SHA |
| `create_pr` | repo/branch/idempotency | delivery permit | protected branch and review gate |

**Đề xuất:** với `execute_command`, ưu tiên allowlisted binary + argument schema; không đưa bash tự do như mặc định ở môi trường rủi ro cao. User có thể cấp sandbox debug shell trong profile giới hạn, không có host credentials/network.

## 5. Context engineering

Context cần phân lớp:

- `system policy summary`: chỉ mang tính hướng dẫn; policy thật ở gateway.
- `mission context`: objective, acceptance, risk, constraints.
- `repo snapshot`: file map và top relevant chunks có commit SHA.
- `tool results`: structured + bounded, logs bị cắt kèm artifact ref.
- `failure context`: test failures, diff, current hypothesis.

Khi context vượt giới hạn, tóm tắt phần cũ nhưng giữ immutable records ngoài model; không bỏ tool result chưa được acknowledgment. Tóm tắt được gắn `source ids` để tránh tạo sự thật không nguồn. Mỗi step phải revalidate budget và scope.

## 6. Sandboxing

V0: container riêng/workspace riêng/UID không đặc quyền, filesystem read-only ngoại trừ workspace, không mount Docker socket, không host network, CPU/memory/time limits, egress allowlist, no ambient secrets, disk quota, cleanup và artifact extraction. **Docker đơn lẻ không bảo đảm mạnh cho code thù địch**; nếu cần multi-tenant untrusted code có thể cân nhắc microVM/hardened sandbox và threat-model lại. Không tự claim “an toàn tuyệt đối”.

## 7. Model routing and fallbacks

Model router tối ưu theo `capability support`, `historical outcome quality`, `latency`, `cost`, `privacy policy`, `provider availability`; không dựa tên model. Fallback phải giữ data boundary và tool semantics; nếu chuyển nhà cung cấp thì kiểm tra quyền gửi dữ liệu và chấp nhận điều kiện audit.

## 8. LLM provider tests

- Endpoint auth, model existence, health, explicit tool-call sample.
- Tool arguments malformed, unknown tool, empty assistant response.
- Parallel tool calls không được hỗ trợ, long context, truncation.
- Rate limit, timeout, 5xx, invalid usage, partial streaming.
- Prompt injection từ file/lệnh, biến tool results thành instructions.
- Fail-closed khi tool calling không tương thích.

## 9. Runtime cost & stopping rules

Một loop phải dừng khi: verifier accepted, no progress, same tool failure repeated, mission budget exhausted, irreversible action requested, policy denied repeatedly, or owner revoked. Ghi lý do. Stopping criteria phải là chương trình ngoài LLM, không phải prompt bảo “hãy tự dừng”.

## 10. API compatibility là một lớp thay thế, không phải USP

Lợi thế của AEO không nằm ở base URL; đó là phần hạ tầng. USP cần được chứng minh ở Opportunity Quality, Decision Ledger, Outcome Evidence và Capability Transfer. Xem [Function calling](https://developers.openai.com/api/docs/guides/function-calling) để tham khảo giao thức OpenAI; endpoint khác vẫn cần kiểm thử thực tế.
