# 27B — Model management và OpenAI-compatible interoperability

## 1. Những thành phần cần tách riêng

`ProviderConfig` (endpoint, secret ref, contract capabilities); `ModelProfile` (model ID, context/output limits, latency/cost metadata); `InvocationPolicy` (data sensitivity, timeout, tools, rate, stop); `ModelRun` (messages digest, response digest, usage, errors, tool calls); `ModelEvaluation` (benchmark results by task class).

Đừng nhúng base URL vào mọi agent; worker hỏi `ProviderGateway` theo profile có version. Một model mạnh cho coding có thể yếu khi phân loại alert, nhưng không routing tự động khi chưa đủ eval.

## 2. API compatibility probe

Nút Test Connection phải kiểm tra độc lập:

- DNS/TLS/host allowlist và status.
- Basic chat completion trả role/content đúng cấu trúc.
- Tool/function call với schema nhỏ và response có tool ID, arguments parse được.
- Tool result round-trip (không chỉ model trả tool call một lần).
- Error handling: rate limit, timeout, invalid model.
- Usage/token fields có thực không; nếu thiếu thì cost chỉ ước tính.
- Context length và output token behavior qua configuration contract.

Nếu provider không hỗ trợ tool-calling, lưu `capability: unavailable`, không thử parse lệnh nguy hiểm từ plain text. Nếu `parallel_tool_calls` không đảm bảo, serialize at gateway.

## 3. Provider failure & privacy

Profile có `classification_allowlist`, `allowed_organizations`, `region`, `contract_status`, `retention_policy_ref`. Với API bên thứ ba, xác minh điều kiện xử lý dữ liệu trước khi gửi source code khách hàng. Endpoint “OpenAI-compatible” chỉ nói về wire format, **không** đảm bảo bảo mật, retention, locality, reliability hay tool semantics.

## 4. Model identity và version drift

Một model ID có thể trỏ phiên bản thay đổi theo thời gian. Lưu `reported_model`, `provider`, `request profile`, prompt version, known eval snapshot. Nếu không pin được physical model version, đánh dấu `MODEL_UNPINNED`; tăng frequency regression tests. Không so sánh before/after chỉ dựa model ID giống nhau.

## 5. Retry và idempotency

LLM response không luôn deterministic; retry sau timeout có thể tạo tool calls khác. Chỉ retry call **trước** khi dispatch side effects; nếu đã nhận tool call và đang thực thi, lưu `tool_call_id` và outcome để không gọi lại. Provider routing fallback không được tự gửi dữ liệu sang provider chưa được cấp quyền.

## 6. Cost accounting

Bảng `model_usage` lưu request count, input/output token khi có, observed usage, price lookup version, estimated cost và invoice reconciliation. Nếu actual billing chưa có, label dashboard `ESTIMATED`, không dùng làm hard cap duy nhất. Thêm caps theo time/requests/steps/sandbox ngay cả khi giá model unknown.

## 7. Provider API and admin UI

`POST /providers` admin-only; `POST /providers/test` with audit; `PATCH /providers/{id}` optimistic concurrency; `GET /providers/{id}` masked secrets; `POST /providers/{id}/revoke` immediate block; `GET /providers/{id}/evals` by job type. Secrets stored in vault, không copy vào mission event snapshots.

## 8. Multi-model strategy

**V0:** one provider one model. **V1:** separate planning/executor/verifier role profiles if benchmark supports. **Later:** routing based on quality/cost and risk. Independent verification ưu tiên deterministic tools/tests hơn chỉ thêm một model reviewer.

## 9. Không phụ thuộc SDK

Tạo interface `complete(messages, tools, config) -> ResponseWithToolCalls` và adapter cho OpenAI-compatible Chat Completions. Không gắn business logic vào format thô. Mỗi adapter có conformance tests và capability registry, phân biệt `unsupported` với `provider_unavailable`.
