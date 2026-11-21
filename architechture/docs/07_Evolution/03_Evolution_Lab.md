# 20 — Evolution Lab: thực nghiệm có đối chứng và chống tự đánh giá

## 1. Vai trò

Evolution Lab là môi trường **không có credential production** để kiểm nghiệm: workflow mới, capability mới, model mới, prompt routing, sandbox policy và scheduling heuristic. Mọi thay đổi đi theo `hypothesis → experiment → analysis → approval → staged promotion → monitor/rollback`.

## 2. Experimental unit

Một unit là `task fixture + repository snapshot + oracle + resource budget + environmental image + seed/order metadata`. Mọi fixture có provenance, data license và cách dựng trạng thái ban đầu. Snapshot đóng băng giữ reproducibility đầu vào, nhưng output model có randomness nên chạy nhiều lần và báo phân phối.

## 3. Baselines

1. **Simple agent:** native single-agent, không World Model/Capability.
2. **Agent + retrieval:** cho truy xuất repo context, không organizational learning.
3. **AEO full candidate:** có goal, opportunity, policy, capability.

Chỉ so sánh trên cùng workload/quality gates, cùng model hoặc ghi rõ khác model. Cần phân biệt gain từ model mạnh hơn với gain từ tổ chức.

## 4. Experiment types

- **Opportunity relevance study:** experts đánh giá mù danh sách cơ hội, phân biệt alert noise.
- **Transfer study:** capability học từ project A, test trên project B khác stack/domain conditions.
- **Policy resilience:** prompt injection, privilege requests, poisoned logs.
- **Long-horizon chaos:** worker kill, timeout, duplicate webhooks, stale branches.
- **Budget policy:** throttling/scheduler fair share, human attention overrun.
- **Outcome monitoring:** synthetic canary + known regression oracle; chưa đủ production causal claim.

## 5. Bias & leakage

Dataset chia train/dev/test theo **project, time và root cause**, không chỉ random task rows. Nếu một bug được nhân bản thành 20 test cùng stack, không coi 20 independent successes. Không sử dụng hidden acceptance cases trong agent context; giữ immutable fixture manifests và audit prompts được gửi.

## 6. Analysis plan

Báo cáo tỷ lệ pass kèm confidence interval hoặc uncertainty ước tính phù hợp với sample size; median/p90 runtime/cost; effect size; failure severity; human review minutes. Không rút kết luận từ 3 ca thành công. Với paired design, cùng fixture chạy hai phương án nhưng cô lập state và randomize order.

## 7. Promotion gates

```text
Test pass + Policy pass + No privacy breach + Baseline uplift/neutral quality
       ↓
Human review of evidence & applicability
       ↓
Canary on allowed low-risk workflows
       ↓
Monitor drift/regressions/cost
       ↓
Promote broadly OR rollback/quarantine
```

Không có policy tự động tự phê chuẩn bản thân. Evaluator/tests được cấp quyền độc lập khỏi capability candidate.

## 8. Tại sao Evolution Lab là USP?

Nhiều hệ thống nói “agent tự học”. Evolution Lab tạo ra **cơ chế falsification**, nơi các thay đổi bị bác bỏ khi không tạo cải thiện thực. Giá trị tích lũy nằm ở *verified operating procedures* chứ không phải summary chat.

## 9. Báo cáo cuối kỳ

Mỗi experiment xuất `experiment.md`, `dataset_manifest.json`, `environment_digest`, `runs.csv`, `analysis.md`, `decision.md`, `incidents.md`, `promotion_record`. Không nhắc “độ thông minh tăng” trừ khi có kết quả held-out và kiểm tra confounders.
