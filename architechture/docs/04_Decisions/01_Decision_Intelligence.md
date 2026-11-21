# 10 — Decision Intelligence: lựa chọn có giải thích, có phản đề, có quyền

## 1. Quyết định không phải chỉ là output JSON của LLM

Decision Engine gồm 4 tầng: `Candidate generation` (LLM/rules), `Eligibility` (policy), `Evaluation` (value/cost/risk/uncertainty), `Commit & Accountability` (phiên bản, audit, mission authorization). LLM được đề xuất, không là điểm cấp quyền cuối cùng.

## 2. Decision record

```json
{
  "decision_id":"dec_001",
  "goal_versions":["goal_checkout_reliability@7"],
  "world_snapshot_id":"ws_0042",
  "opportunity_ids":["opp_117","opp_122"],
  "selected":"opp_117",
  "alternatives":[{"id":"opp_122","reason":"lower expected impact"},
                  {"id":"NONE","reason":"low risk of waiting but SLO burn rising"}],
  "policy_eval_id":"pol_eval_991",
  "risk_class":"low",
  "resource_limit":{"usd":12,"minutes":60},
  "evidence_refs":["evi_04","evi_29"],
  "uncertainty":"medium",
  "human_override":false,
  "status":"COMMITTED"
}
```

Record phải có input digest, model/version của candidate step, policy version, owner, time và eventual outcome. Decision re-evaluation tạo record mới và `supersedes`; không ghi đè lịch sử.

## 3. Decision types

- `DO_NOTHING`: không hành động khi không đủ giá trị/evidence, nhưng định thời review.
- `GATHER_EVIDENCE`: điều tra read-only hoặc sandbox test.
- `PROPOSE_MISSION`: xin mission warrant.
- `ESCALATE`: human cần cân nhắc trade-off/permission.
- `DEFER`: đủ cơ sở nhưng chưa ưu tiên.
- `CANCEL/REPLAN`: điều kiện nền thay đổi.

## 4. Uncertainty decomposition

**Epistemic**: chưa biết root cause; có thể giảm bằng thông tin. **Aleatoric**: traffic biến động tự nhiên; không xóa bằng đọc thêm docs. **Model uncertainty**: parser/model sai hoặc version drift. **Policy ambiguity**: scope, ownership hoặc contract chưa rõ. AEO phải biết loại nào cần giải pháp nào; mặc định `more LLM calls` không luôn tăng tin cậy.

## 5. Value of Information (VOI)

Khi khả năng hành động sai và thiệt hại cao, AEO nên cân nhắc điều tra trước. Ý tưởng VOI: `Expected value after observation - value before observation - cost of obtaining observation`. Không yêu cầu tính chính xác bằng một scalar; trong V0 tạo heuristic: nếu `unknown critical dependency` và `change affects payment`, điều tra/approval trước.

## 6. Risk classification

Tách `impact severity`, `blast radius`, `reversibility`, `data sensitivity`, `uncertainty`, `exposure`.

| Risk | Ví dụ | Autonomy tối đa mẫu |
|---|---|---|
| R0 | Phân tích logs đã redact, query metadata | Read-only |
| R1 | Test branch, sửa docs/test, PR | Branch-only |
| R2 | Merge thay đổi trên staging với canary | Approval + automation |
| R3 | Payment logic, schema migration, prod rollout | Human authorization bắt buộc |
| R4 | Xóa dữ liệu prod, sửa quyền root, chuyển secrets | Deny/default exceptional process |

Các mức là **[DESIGN]** và phải hiệu chỉnh theo chính sách doanh nghiệp.

## 7. Falsifiability

Mỗi decision quan trọng trả lời:

- Điều gì sẽ chứng minh giả thuyết sai?
- Metric nào thay đổi sau thực thi, kiểm soát confounders ra sao?
- Không có cải thiện thì có revert, giữ nguyên hay chạy lại thử nghiệm?
- Nếu không làm, dự đoán rủi ro cụ thể là gì?
- Ai chịu trách nhiệm review các kết quả không như dự kiến?

## 8. Cách đánh giá decision quality

- Hindsight review có kiểm soát: decision có hợp lý **với evidence tại thời điểm ra quyết định** hay không, không chỉ dựa outcome.
- `Calibration`: trong nhóm dự đoán success probability p, tỷ lệ thành công có tương ứng không? Chỉ làm nếu đủ mẫu.
- `Regret`: chênh lệch giá trị so với lựa chọn tốt nhất có thể, thường chỉ ước tính nên phải ghi giới hạn.
- `Policy compliance`: tuyệt đối không coi tỷ lệ vi phạm thấp là chấp nhận được với high-severity.
- `Explanatory sufficiency`: reviewer có thể tái dựng vì sao chọn mission.

## 9. Quyền human override

Con người có thể `approve`, `reject`, `change_priority`, `request_more_evidence`. Override phải lưu reason code; dữ liệu đó có thể cải thiện scoring, nhưng không auto train từ mọi override (override đôi khi có chủ đích chính trị/doanh nghiệp mà không phản ánh truth kỹ thuật).
