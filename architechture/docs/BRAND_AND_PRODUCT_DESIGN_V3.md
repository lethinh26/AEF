# AEO — Brand & Product Design System v3

**Hướng thiết kế:** *Quiet Authority / Architectural Operations*  
**Phiên bản:** Concept 3 — 21/11/2026  
**Phạm vi:** AEO Control Center, Living World, Goal OS, Mission Control, Production Studio, Evolution Lab.  
**Tình trạng:** Đề xuất thiết kế để duyệt; chưa phải logo được phê duyệt hoặc sản phẩm có backend.

## 1. Điều cần sửa — tại sao giao diện trước dễ bị nhận ra là “AI làm”

Một sản phẩm bị cảm nhận là “AI-generated” thường không do dùng AI để thiết kế, mà do thiếu quyết định biên tập: các card giống nhau, mọi thành phần đều được bo góc, icon rập khuôn, gradient và glow không có mục đích, nội dung giống số liệu demo, các phần không có điểm nhìn ưu tiên, ngôn ngữ quảng cáo đặt vào màn hình vận hành và 3D tạo hiệu ứng thay vì diễn đạt sự thật.

Mục tiêu v3 **không** phải làm giống giao diện của một thương hiệu khác. Mục tiêu là một ngôn ngữ riêng, trưởng thành, chính xác, khiến người vận hành hiểu tình trạng trong vài giây và cảm thấy tin tưởng vào các quyết định của AEO.

**Định vị thẩm mỹ:** Nhà điều hành hạ tầng kỹ thuật + bản vẽ kiến trúc + phần mềm nghiên cứu/chế tạo chuyên nghiệp. *Không phải:* AI assistant landing page, game sci-fi, startup neon dashboard.

## 2. Năm nguyên tắc bất biến

1. **One focal point:** Mỗi màn hình có đúng một vùng trọng tâm, các thành phần hỗ trợ chỉ đóng vai trò giải thích và hành động.
2. **Content before chrome:** Trạng thái thật, nguồn và điều kiện kiểm chứng phải xuất hiện trước các yếu tố trang trí.
3. **Precision, not symmetry at all costs:** Dùng lưới có nhịp, nhưng thay đổi tỷ lệ có lý do; không biến mọi thứ thành lưới card 4 cột bằng nhau.
4. **Quiet motion:** Mọi animation gắn với sự kiện có timestamp; không loop vô nghĩa để giả vờ có AI đang suy nghĩ.
5. **Human review:** Mỗi màn hình phải qua kiểm tra thiết kế với dữ liệu thật, nội dung dài/ngắn, lỗi, loading, trống, màn hình nhỏ; không chỉ render một screenshot đẹp.

## 3. Brand identity: giữ màu v2, thay cách sử dụng

| Token | HEX | Chức năng |
|---|---|---|
| Ink | `#101D2E` | Logo, heading, scene dark mode |
| Deep navy | `#18283B` | Các bề mặt dark mode |
| Corporate blue | `#2457A7` | Hành động chủ đạo và vùng được chọn; <10% diện tích UI |
| Graphite | `#303A46` | Nội dung phụ |
| Slate | `#46556A` | Chú thích, dữ liệu |
| White | `#FFFFFF` | Mặt chính |
| Cloud | `#F7F9FC` | Nền |
| Border | `#DCE3EB` | Divider/ranh giới |
| Success | `#167347` | Đã xác minh |
| Warning | `#9A6700` | Cần quyết định/đánh giá |
| Danger | `#B42318` | Lỗi, từ chối, vi phạm |

**Không dùng:** gradient cầu vồng, sáng neon, tím cho AI, blue-glow trên toàn màn hình, giọt kính mờ, drop shadow lớn. 3D dùng các cấp độ slate và ánh sáng trung tính; xanh chỉ cho đối tượng đang được chọn.

### Logo

Giữ hướng **AEO wordmark thuần hình học**, chữ navy với độ dày vừa phải. Icon app tạm thời dùng chữ `A`/`AEO` trên nền phẳng. Không thêm hình robot, chip, brain, sparkle. **Không chốt logo chỉ bằng một bản dựng nhanh**: cần vòng refinement về kerning, tỷ lệ ký tự và thử ở 16/24/32/128px. Chưa xác minh nhãn hiệu.

## 4. Typography và bố cục

- Primary: **Inter** hoặc **IBM Plex Sans** sau khi kiểm tra hỗ trợ tiếng Việt; không pha 3–4 họ font.
- Secondary mono: **IBM Plex Mono** cho mã job, commit SHA, timestamp, metric có tabular numbers.
- Heading chủ đạo desktop 29–34px / `letter-spacing: -0.03em`, text thường 14–15px; không viết toàn bộ tiêu đề tiếng Việt bằng uppercase tracking rộng.
- Sidebar cố định ~210px; nội dung chính fluid; vùng 3D là nhân vật chính, không ép 3D vào một card bé.
- Bố cục ưu tiên 2 cột bất cân xứng **70/30**: world canvas + contextual inspector. Các số liệu chỉ nằm trong một dải đo lường gọn, không dùng 4 KPI cards to như khuôn mẫu.
- Radius: 0–6px cho nội dung nghiệp vụ; 6–8px cho kiểm soát. Vạch phân cách mảnh tốt hơn nhiều bóng đổ.
- 8pt spacing grid, nhưng có nhịp trống 24/32/48 để thiết lập phân cấp.
- Tối thiểu WCAG AA cho thông tin quan trọng, tương tác bàn phím, chú thích trạng thái bằng chữ ngoài màu.

## 5. 3D: architectural information, not entertainment

Living World là **bản đồ tổ chức 3D có ngữ nghĩa**, không phải thành phố đồ chơi. 3D nên có dáng kiến trúc và ngôn ngữ biểu đồ kỹ thuật:

- Mỗi công trình đại diện cho một **năng lực tồn tại thật** của AEO, không nhất thiết là một agent.
- Tỷ lệ thống nhất, góc camera orthographic/isometric vừa phải, vật liệu matte concrete/steel/smoke glass tiết chế.
- Đường kết nối chỉ có khi có dependency/mission được ánh xạ thực; không vẽ các luồng năng lượng ngẫu nhiên.
- Chọn một công trình: camera tập trung nhẹ và panel hiển thị mission, trạng thái, bằng chứng, timestamp, quyền hạn.
- Chỉ biến đổi hình học khi mang thông tin (đang xử lý, dừng, bị chặn); không “nhấp nháy đang suy nghĩ”.
- Hoạt ảnh theo *event replay*: có lịch sử và timeline, dừng được, đồng bộ event ID.
- 3D chỉ là **một góc nhìn** của một trạng thái chuẩn có thể truy vấn qua API và mở dưới dạng bảng 2D.
- Mỗi màn hình hiển thị `LIVE / REPLAY / DEMO / STALE` không thể nhầm lẫn.

**Cấm làm 3D đẹp nhưng thiếu thông tin:** người dùng phải trả lời được trong 5 giây: tổ chức đang làm gì, thành phần nào có vấn đề, việc gì cần họ xử lý, và vì sao.

## 6. Quy tắc UI giảm cảm giác “AI-template”

| Tránh | Thay bằng |
|---|---|
| Four metric cards đồng kích thước | Một dải summary nhỏ + 1 vùng công việc trọng tâm |
| Hero marketing kiểu “Engineering, reinvented.” trong sản phẩm | Heading đúng nhiệm vụ: “Tổ chức” / “Hoạt động hôm nay” |
| 3D neon chạy vô hạn | Scene đọc từ event và trạng thái, freeze khi không có sự kiện |
| Avatar robot / icon brain / sparkle | Icon tác vụ ngữ nghĩa: xét duyệt, phiên chạy, lỗi, bằng chứng |
| Hàng chục badge màu | Tối đa vài trạng thái thực sự đáng phân biệt |
| Placeholder giả vờ dữ liệu thật | Đặt nhãn DEMO và mốc thời gian cụ thể |
| Glow / shadow / gradient tất cả | Sử dụng đường kẻ, độ tương phản, khoảng trắng |
| Phủ 3D lên bảng code và logs | Inspector 2D cho dữ liệu kỹ thuật, code diff, approval |
| Hoạt ảnh vô căn cứ | 150–280ms cho phản hồi tương tác; các sự kiện replay có điểm đầu/cuối |

## 7. Sáu màn hình bắt buộc thiết kế bằng cùng một nguyên tắc

**Organization:** world lớn, một danh sách công việc cần chú ý, nguồn và thời điểm đồng bộ.  
**Mission Focus:** cấu trúc thực thi, trace, kiểm chứng, diff, khả năng hủy và ngoại lệ.  
**World Model:** bản đồ phụ thuộc thực, bộ lọc lớp dữ liệu, provenance, mốc làm mới.  
**Goal OS:** chỉ số mục tiêu, error budget / SLA, Opportunity liên quan, owner và policy.  
**Production Studio:** brief, nguồn tư liệu, acceptance contract, preview/đánh giá theo milestone.  
**Evolution Lab:** thí nghiệm cạnh nhau, split run, score, confidence, data leakage checks, approve/rollback.

## 8. Interaction blueprint

- App shell: persistent nav, breadcrumb, realtime indicator, keyboard search `⌘K`, account & org switch.
- World canvas: click/tap chọn, scroll zoom, drag pan, `Reset view`, keyboard accessible list view.
- Inspector: hiện `what / why / when / evidence / next action` cho thực thể đang chọn.
- Approval: lý do, phạm vi quyền, blast radius, phương án rollback và bằng chứng đi cùng nút duyệt/từ chối.
- Empty/loading/error: có trạng thái riêng, không dựng demo data giả khi kết nối backend thất bại.
- Accessibility: reduce motion, contrast, keyboard navigation, mobile list view.

## 9. Vận hành & thiết kế kỹ thuật

Ứng dụng đề xuất: Next.js + React + TypeScript + CSS tokens, React Three Fiber/Three.js cho world thật, Zustand cho trạng thái lựa chọn/presentation, TanStack Query cho server state, SSE/WebSocket cho sự kiện, FastAPI backend. Event-to-visual mapper chuẩn hóa domain events thành UI states. Không để logic quyền hạn và sự thật nghiệp vụ nằm trong renderer.

Cần instrument: time-to-understand, task completion time, false impression (người dùng tưởng agent đang chạy khi thật ra idle), approval error rate, FPS, input latency, renderer memory. Đánh giá 5–7 người ở các vai trò kỹ thuật khác nhau với tác vụ thực và câu hỏi “Bạn hiểu điều gì đang xảy ra?”.

## 10. Quy trình thiết kế có chủ đích

1. Dùng 3–5 dữ liệu tình huống thật, dựng **information hierarchy wireframe** trước khi tô màu.
2. Thiết kế độc lập **Organization / Mission / Approval** desktop trước; responsive là biến thể có mục đích chứ không co các card xuống.
3. Art direction 3D: kiểm tra silhouette đơn sắc, tương quan góc nhìn, label legibility trước khi thêm vật liệu.
4. Tinh chỉnh thủ công typography, khoảng cách, border, icon, các trạng thái đặc biệt.
5. Kiểm thử giảm motion, keyboard, Vietnamese long text và real timestamp.
6. Test với người dùng: không hướng dẫn trước; yêu cầu tìm một mission lỗi và giải thích lý do cần duyệt.
7. Tinh chỉnh theo kết quả, không chốt vì một screenshot đẹp.

## 11. Definition of Done cho giao diện

- [ ] Trong 5 giây, thấy được trạng thái vận hành, 1 mối quan tâm chính và next action.
- [ ] Có bằng chứng và thời gian cập nhật, hoặc nhãn Demo rõ ràng.
- [ ] Không có animation “chạy giả” khi backend idle/offline.
- [ ] World và inspector hiển thị cùng một entity state.
- [ ] Mọi thao tác quan trọng có bản hiển thị 2D tương đương.
- [ ] Brand colors/tokens nhất quán; visual contrast và focus states đạt chuẩn.
- [ ] Các tác vụ phổ biến hoàn thành trong <=3 tương tác có ý nghĩa sau khi mở màn hình.
- [ ] Giao diện đã được designer review bằng dữ liệu có thật/giả lập trung thực, không chỉ bằng mock marketing.

## 12. Lưu ý về concept đi kèm

File `aeo-design-preview.html` là **prototype thị giác 2.5D** tự chứa, trình bày cách tổ chức thông tin. Nó không phải engine 3D thật và không kết nối backend. Bản production cần render WebGL và đồng bộ dữ liệu theo state/event contracts.
