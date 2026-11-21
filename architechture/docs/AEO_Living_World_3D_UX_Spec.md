# AEO Living World — 3D Experience & Real-time Digital Twin Specification

**Trạng thái:** UX/Architecture Proposal v0.1 · **Ngôn ngữ:** Tiếng Việt · **Mục đích:** định nghĩa trải nghiệm trực quan cho Autonomous Engineering Organization (AEO).

> Bản thiết kế này mô tả sản phẩm mục tiêu. [AEO_Living_World_3D_Prototype.html](./AEO_Living_World_3D_Prototype.html) chỉ là demo 3D isometric được dựng bằng Canvas, với dữ liệu mô phỏng, chưa tích hợp backend. Trong triển khai thực, đề xuất dùng Three.js/React Three Fiber (WebGL).

## 1. Triết lý sản phẩm

AEO không phải một IDE, không phải một dashboard KPI, không phải trò chơi. Đó là **bản sao trực quan của một tổ chức kỹ thuật đang hoạt động**: digital twin dùng trạng thái hệ thống thực để biểu diễn người máy/nhóm năng lực, Mission, sự kiện, quyết định, bằng chứng, sự cố và tiến hóa năng lực.

Câu hỏi sản phẩm phải trả lời trong vòng năm giây sau khi mở giao diện:

1. **Tổ chức có khỏe không?** Bao nhiêu hệ thống trong phạm vi trách nhiệm ổn định / đang có sự cố / mất tín hiệu?
2. **AEO đang làm gì?** Công việc nào đang hoạt động, vì sao nó được bắt đầu, đã đi tới đâu?
3. **Tôi cần can thiệp vào đâu?** Phê duyệt, làm rõ yêu cầu, giải quyết xung đột, vượt ngân sách hoặc sự cố nào?

Câu hỏi tiếp theo phải trả lời trong tối đa hai lần nhấp: *vì sao làm việc đó, bằng chứng nào ủng hộ, chi phí và rủi ro nào, đã tạo ra thay đổi gì, khi nào được phép triển khai?*

Nguyên tắc: **3D là không gian điều hướng, thông tin chính xác vẫn là dữ liệu tương tác có thể tra cứu**. Không mô phỏng từng token, từng suy nghĩ của model hoặc phóng đại năng lực bằng hoạt cảnh không có sự kiện tương ứng.

## 2. Bố cục không gian ba tầng

### Tầng L0 — Organization World

Góc nhìn isometric/orthographic, thấy một campus số gồm bảy khu chức năng:

| Zone | Hình tượng 3D | Ý nghĩa | Nguồn dữ liệu |
|---|---|---|---|
| Radar / Sensing | Tháp radar, vòng quét | Thu thập và đối chiếu tín hiệu | CI, monitoring, Git, issue trackers |
| World Model | Thư viện dữ liệu, khối cấu trúc | Thực thể, quan hệ, độ tin cậy | Entity graph, observations, provenance |
| Goal & Decision Nexus | Trung tâm chiến lược | Mục tiêu, cơ hội, chọn Mission | Goal OS, Opportunity, Decision Ledger |
| Execution Workshop | Xưởng robot/khối năng lực | AI agents, tools, sandbox runs | Agent runtime, tool events |
| Verification Lab | Lab kiểm chứng | Tests, benchmarks, release gates | Test runners, CI, evidence artifacts |
| Delivery Dock | Trạm bàn giao | PR, staging, artifacts, approval | Git provider, delivery service |
| Evolution Forge | Xưởng thử nghiệm | Capability candidates, đánh giá A/B | Capability registry, eval runs |

Không nên biểu diễn mỗi agent thành người máy đi bộ liên tục; chúng có thể là các chùm sáng, module chạy, “worker pods” xuất hiện khi task thực sự được cấp phát. Số lượng agent và khu vực có thể thay đổi nhưng ngôn ngữ không gian phải ổn định.

### Tầng L1 — Project/Goal World

Nhấp vào mục tiêu hoặc một hệ thống sẽ zoom vào một campus con: services, databases, pipelines, phụ thuộc, health state và Mission tác động tới hệ thống đó. Chỉ hiển thị những quan hệ có bằng chứng; quan hệ suy luận chưa xác minh dùng đường đứt nét.

### Tầng L2 — Mission Floor

Nhấp Mission sẽ đi vào một “production line” gồm các trạm: evidence intake → analysis → decision → plan → execution → verification → repair/approval → delivery → observation/evolution. Hình khối đại diện nhiệm vụ, luồng và kết quả; chi tiết code, diff, logs, traces vẫn có bảng điều khiển phía bên cạnh.

### Tầng L3 — Evidence/Technical Inspector

Không cần một cảnh 3D thứ tư. Hiển thị inspector 2D cho dữ liệu khó đọc trong không gian 3D: logs, patch, test report, trace, policy, model usage, dependency graph có thể lọc và bản so sánh trước/sau.

## 3. Các phép ánh xạ hình ảnh phải có quy tắc

| Trạng thái hệ thống | Hình ảnh | Chữ/biểu tượng đi kèm | Nguồn xác nhận |
|---|---|---|---|
| IDLE | Tòa nhà sáng nhẹ, ít chuyển động | Chờ | State store |
| QUEUED | Mission capsule tại cửa vào | Xếp hàng | Scheduler event |
| RUNNING | Máy hoạt động, luồng sáng di chuyển | Đang chạy + bước cụ thể | Worker started/tool dispatched |
| VERIFYING | Luồng chuyển tới Verification Lab | Đang kiểm thử | Test runner started |
| WAITING_APPROVAL | Cổng dừng, cảnh báo màu hổ phách | Cần bạn duyệt | Approval request persisted |
| REPAIRING | Luồng quay về Execution Workshop | Đang sửa lần N/M | Retry attempt event |
| COMPLETED | Capsule về Delivery Dock, dấu kiểm | Đã đạt verification | Signed verification result |
| FAILED | Trạm lỗi có đường viền đỏ, không nhấp nháy quá mức | Lỗi + nguyên nhân | Failure recorded |
| STALE/UNKNOWN | Tòa nhà giảm sáng, biểu tượng “?” | Mất tín hiệu / Chưa rõ | Timestamp/heartbeat TTL |
| PAUSED | Hoạt cảnh đứng yên | Đã tạm dừng | Workflow engine acknowledgement |

Quy tắc bắt buộc: không dùng màu sắc là kênh duy nhất; thêm icon, nhãn và hình dạng. Khi offline hoặc thiếu nguồn dữ liệu, **không tự giả lập là hệ thống vẫn đang chạy bình thường**. Dữ liệu stale có nhãn và thời điểm đồng bộ gần nhất.

## 4. Hành trình người dùng tiêu biểu

**A. 5 giây xem toàn cảnh:** mở web → Organization World → nhận diện 2 vùng có cảnh báo và số Mission đang chạy → bấm vùng cảnh báo → xem lý do và bằng chứng.

**B. 30 giây điều tra công việc:** click capsule hoặc khu Mission → camera bay nhẹ vào production line → panel bên phải hiển thị Goal, Opportunity, decision rationale, active executor, thời gian chạy, chi phí đo được, artifact đang có, next gate → click Evidence để xem test/log/diff.

**C. Phê duyệt an toàn:** click badge cần duyệt → dialog riêng có actor, permission, target, diff/risk, expiration, rollback plan, tác động → quyết định phê duyệt/từ chối; UI chỉ xác nhận thành công sau khi backend áp dụng chính sách và trả acknowledgment.

**D. Xem lại sự cố:** chọn timeline → tua ngược theo event log → UI chuyển sang REPLAY và hiển thị thời gian lịch sử → mở lại causal chain tại thời điểm tương ứng. Không đồng thời trình bày replay như live.

**E. Sản xuất sản phẩm mới:** Production Studio cho phép mô tả ngôn ngữ tự nhiên/Figma/BRD/repository → tạo Goal/Program → scene xuất hiện khu dự án mới → tiến độ module/mission liên kết với acceptance evidence. Không ép người dùng phải điều khiển agent thủ công.

## 5. UI bố trí

- **Top:** AEO brand, LIVE/REPLAY/DEMO, timestamp, hệ thống đang quan sát, kết nối, notifications.
- **Left rail:** Home / Radar / Goals / Mission Control / Projects / Evolution / Policies / Search.
- **Main viewport:** 3D canvas đầy đủ; camera isometric mặc định; click và hover nhất quán, có focus, reset camera, zoom.
- **Right inspector:** chi tiết thực thể đang chọn, hiện hành động, nguyên nhân, trạng thái, KPI, lịch sử, bằng chứng và “next action”.
- **Bottom timeline:** workflow stage, real events, fast scrub/replay, delay/stale indicators.
- **Command palette:** tìm bất kỳ goal/mission/repository/capability bằng tên/ID, nhảy camera tới vị trí.
- **Essential text fallback:** nút chuyển sang “List/Map view”, hỗ trợ keyboard và reduced motion, không bắt buộc dùng 3D để phê duyệt.

Gợi ý art direction: **premium scientific miniature / diorama**; tối navy, ánh sáng mềm cyan–mint, kính mờ, ít neon gây mỏi mắt; không dùng cảnh city quá chi tiết khiến người dùng phải tìm kiếm.

## 6. Kiến trúc frontend đề xuất

```text
Next.js + React + TypeScript
├── World3D (Three.js + React Three Fiber)
│   ├── CameraDirector / Orbit & Zoom controls
│   ├── SceneGraph / ZoneBuilder / MissionCapsules
│   ├── AnimationController (event-driven)
│   ├── Picking & Selection
│   └── LOD / Instancing / PerformanceMonitor
├── Organization Store (Zustand or equivalent)
│   ├── Snapshot reducer
│   ├── Event stream reducer
│   ├── Entity selection & camera state
│   └── Live/replay/demo mode
├── Inspector / Timeline / CommandPalette (regular React HTML)
└── API client (HTTP + SSE; WebSocket if bidirectional demands emerge)
```

- **Three.js / React Three Fiber** dùng trong sản phẩm thật để render mô hình WebGL. Mẫu HTML demo dùng phép chiếu tọa độ 3D lên Canvas 2D, không phải renderer production.
- Dùng Blender để thiết kế low-poly 3D assets và xuất glTF/GLB; không dùng AI sinh cảnh không có quy chuẩn khi cần trạng thái ổn định.
- Dùng camera orthographic để giữ tính rõ ràng và kích thước tương đối nhất quán; hỗ trợ camera presets và focus smooth.
- Text quan trọng nằm trong DOM overlay hoặc HTML inspector để dễ đọc, sao chép, tìm kiếm, trợ năng.
- Dùng Zustand/React Query tuỳ nhu cầu state; không đưa hoạt ảnh 60 fps vào React state, cập nhật Three.js transforms qua animation loop.

## 7. Luồng dữ liệu thật: Event → Twin → Scene

```text
Git / CI / Monitoring / Agent Runtime / Temporal / Verification
       ↓ connectors (trusted ingress, validation, provenance)
Canonical Event Store (append-only) + materialized world state
       ↓ Event Publisher (sequence per aggregate, cursor, replay)
AEO Read API → Snapshot + authenticated SSE stream
       ↓ Client Reducer (dedupe; gap detection; reconciliation)
Visual Twin State (entities, goals, missions, zone status)
       ↓ Visual Mapping Engine (pure deterministic functions)
Scene Graph + event-triggered transitions / camera focus
       ↓
3D digital twin + inspector + timeline + audits
```

Ví dụ event envelope (chỉ minh hoạ hợp đồng, không phải chuẩn cố định):

```json
{
  "event_id": "evt_00942",
  "aggregate_type": "mission",
  "aggregate_id": "mis_042",
  "sequence": 31,
  "occurred_at": "2026-11-21T12:00:00Z",
  "observed_at": "2026-11-21T12:00:01Z",
  "type": "verification.failed",
  "payload": {
    "target": "checkout-api",
    "attempt": 1,
    "max_attempts": 3,
    "verification_id": "ver_082",
    "failed_tests": 1
  },
  "provenance": {"source": "verification-worker", "artifact_ref": "art_151"}
}
```

Client không diễn hoạt “agent đang nghĩ”. Nó chỉ có thể diễn hoạt “LLM request sent/returned”, “tool invocation started/completed”, “file change recorded”, “test run started/completed”, mỗi hành động liên kết với evidence id có thể mở.

**Snapshot + stream handshake:** gọi `GET /world/snapshot` có `cursor` nhất quán; subscribe `GET /world/events?cursor=...`, dedupe theo `event_id`, phát hiện gap `sequence` để sync lại snapshot. Trong replay, tái tạo trạng thái từ snapshot lịch sử và event log, tránh mutate dữ liệu LIVE.

**SSE** đủ tốt cho đẩy cập nhật server → browser giai đoạn đầu; action của người dùng đi qua HTTP API. Dùng WebSocket nếu thực sự cần lệnh/giao tiếp hai chiều tần suất cao.

## 8. Thiết kế Scene Graph và thông tin tránh hiểu sai

- Object chỉ có ID ổn định, binding đến domain entity; không hardcode KPI vào mesh.
- Mọi hoạt ảnh phân thành **transition tied to event** hoặc **decorative ambient**, và phân biệt về ý nghĩa. Ambient không được ngụ ý một job đang chạy.
- Khi job bị timeout, ngừng animation active, hiển thị trạng thái và thời điểm lần cuối nhận tín hiệu.
- Nếu sự kiện đi trễ hoặc đảo thứ tự, reducer áp dụng theo version/sequence, không theo thời điểm đến.
- Không hiển thị phần trăm “AI đã xong” nếu không có nguồn đo tin cậy: ưu tiên `step N/M`, acceptance checks, `runtime elapsed` và trạng thái.
- Trạng thái “đã xong” chỉ khi kết quả verification đạt; “outcome improved” là một thành quả riêng, có đánh giá sau triển khai.
- Hành động pause/stop/approve phải dùng policy, reason và acknowledgement thật; UI optimistic không được giả báo thành công.

## 9. Tối ưu hiệu năng và khả năng tiếp cận

- Model thấp polygon, tái sử dụng mesh/material, instance geometry lặp lại; culling và level-of-detail khi camera xa.
- Texture nén, tải asset theo vùng và có placeholder 2D.
- Thiết bị yếu dùng DPR thấp hơn, render theo nhu cầu khi cảnh không có animation, giới hạn số particle và post-processing.
- Gộp sự kiện nhanh theo batch để animation biểu diễn biến đổi trạng thái, không bắt scene render một frame cho mỗi log line.
- Hỗ trợ `prefers-reduced-motion`, keyboard navigation, screen-reader-friendly HTML table/list view, tương phản màu, nhãn không chỉ màu.
- Mục tiêu cần kiểm chứng bằng test với máy thật: 30–60 FPS desktop trung bình trong hoạt cảnh; thời gian vào view phụ thuộc asset, chưa cam kết số giây cố định.
- Một cảnh quá đông phải gom nhóm theo Goal/Project/Zone, không dựng hàng chục nghìn agent làm các vật thể tương tác riêng.

## 10. Kế hoạch triển khai 3D theo giá trị

**Prototype / UX validation (1–2 tuần thử nghiệm):** demo 3D tương tác, 5–7 khu, camera, Mission animation, inspector, snapshot giả lập. Kiểm tra người không phải dev có hiểu trong 5 giây hay không.

**V0.1 Live Radar (3–5 tuần mục tiêu):** world scene thật, repo/CI connectors, scene mapping, SSE, history/replay, no-code decisions; không giả báo thực thi agent.

**V0.2 Real Missions:** tích hợp workflow/agent execution, mission capsules, logs, tests, approval gates, real event-to-animation, preview diffs.

**V0.3 Evolution & Production:** Evolution Forge / Capability experiments / Product Studio, project-level campus; phân tầng để tránh nhồi mọi dữ liệu vào một màn hình.

Các mốc chỉ là định hướng lập kế hoạch; phạm vi và hạ tầng sẽ quyết định tốc độ thực tế.

## 11. Tiêu chí nghiệm thu bắt buộc

1. Người mới mở sản phẩm tìm được 3 thông tin (health, active work, attention) mà không cần đọc tài liệu.
2. Bấm tối đa hai lần để từ cảnh tổng quan tới evidence của một Mission.
3. Mọi trạng thái “RUNNING”, “FAILED”, “DONE”, “WAITING_APPROVAL” trên cảnh có thể truy nguồn từ event hoặc snapshot.
4. Khi mất kết nối, toàn bộ scene cho biết dữ liệu không còn live.
5. Trong replay, không có chỉ báo “LIVE” gây nhầm lẫn.
6. Quyền mới chỉ được cấp khi backend policy xác nhận; UI chỉ phản ánh.
7. Người dùng không cần WebGL vẫn thực hiện được các thao tác quan trọng qua chế độ 2D.
8. Animations tắt được; keyboard và trình đọc màn hình có đường sử dụng chính.
9. Đa dự án vẫn dễ quan sát nhờ hierarchy; một mission không làm cả scene chớp nháy.
10. Thực hiện usability testing với ít nhất 5 người dùng đại diện trước khi mở rộng art assets.

## 12. Rủi ro thiết kế

- **3D theater:** animation đẹp nhưng không gắn event → mất lòng tin.
- **Information overload:** quá nhiều tòa nhà/agent, quá khó tìm thứ quan trọng → hierarchy + camera presets + search.
- **False progress:** progress suy đoán không có bằng chứng → dùng trạng thái/gates thay cho số % tùy tiện.
- **“AI thinking” anthropomorphism:** suy diễn trạng thái nội tâm không quan sát được → thể hiện tool/events có nguồn.
- **Security exposure:** mô hình 3D không được lộ source code/private project name cho người thiếu quyền → ACL tại API và streaming, không chỉ ẩn trên UI.
- **Misleading live status:** nhận sự kiện trễ hoặc không nhận heartbeat → hiển thị stale.

## 13. Nguồn tham khảo kỹ thuật

- React Three Fiber performance: https://r3f.docs.pmnd.rs/advanced/scaling-performance
- Three.js Raycaster: https://threejs.org/docs/pages/Raycaster
- MDN SSE: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- Siemens Opcenter X Intosite: https://www.siemens.com/en-us/products/opcenter/opcenter-x-intosite/

**Tóm tắt:** AEO Living World nên là *digital twin thật* của một tổ chức kỹ thuật, không phải mascot/3D dashboard trang trí. Giá trị được kiểm chứng bằng khả năng hiểu nhanh tình trạng, truy ngược bằng chứng và quản lý hành động đúng quyền hạn.
