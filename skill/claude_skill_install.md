Dưới đây là bản tổng hợp và hướng dẫn chi tiết về các công cụ mạnh mẽ nhất trong hệ sinh thái **Claude Code** tính đến năm 2026. Bản hướng dẫn này được thiết kế để giúp bạn biến Claude từ một chatbot thành một kỹ sư phần mềm thực thụ.

---

## 🛠️ Các công cụ cốt lõi (Core Ecosystem)

### 1. Superpowers (obra)

**Mô tả:** Framework chuẩn hóa quy trình làm việc. Nó ép AI phải tuân thủ kỷ luật: Brainstorm -> Lập kế hoạch -> Viết Test (TDD) -> Code.

* **Cài đặt:**
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

```


* **Cách sử dụng:**
* Sử dụng `/superpowers:brainstorm` để thảo luận thiết kế trước khi code.
* Dùng `/superpowers:write-plan` để AI chia nhỏ tác vụ thành các task 2-5 phút.
* Dùng `/superpowers:execute-plan` để AI tự động thực hiện và chạy test.



### 2. agents (wshobson)

**Mô tả:** Kho gồm hơn 100 agent chuyên biệt (Python, DevOps, Security...). Bạn không cần nạp mọi thứ, chỉ cài "chuyên gia" bạn cần để tiết kiệm token.

* **Cài đặt:**
```bash
/plugin marketplace add wshobson/agents
/plugin install [tên-plugin] # Ví dụ: python-development hoặc security-scanning

```


* **Cách sử dụng:** Triệu hồi các agent chuyên biệt bằng cách đề cập tên họ hoặc dùng lệnh:
* Ví dụ: `/python-development:python-scaffold` để tạo cấu trúc dự án chuẩn.



### 3. claude-mem (thedotmack)

**Mô tả:** Giải quyết vấn đề "mất trí nhớ" của AI sau mỗi phiên làm việc. Nó ghi lại nhật ký, nén bằng AI và tự động nạp lại ngữ cảnh cũ khi bạn quay lại dự án.

* **Cài đặt:**
```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem

```


* **Cách sử dụng:** * Hoạt động tự động ngầm.
* Bạn có thể xem "dòng suy nghĩ" của AI tại `http://localhost:37777`.
* Tra cứu quá khứ bằng lệnh: `/mem-search "lần trước tôi đã sửa lỗi auth như thế nào?"`



### 4. planning-with-files (OthmanAdi)

**Mô tả:** Lưu kế hoạch làm việc vào file `.md` trong project. Điều này giúp cả bạn và AI luôn nhìn thấy mục tiêu chung, không bị lạc đề khi hội thoại quá dài.

* **Cài đặt:**
```bash
/plugin marketplace add OthmanAdi/planning-with-files
/plugin install planning-with-files@planning-with-files

```


* **Cách sử dụng:**
* Gõ `/planning-with-files` để bắt đầu lập kế hoạch.
* AI sẽ tạo các file như `task_plan.md`, `findings.md`. Bạn có thể chỉnh sửa các file này để điều hướng AI.



### 5. oh-my-claudecode (Yeachan-Heo)

**Mô tả:** "Đao to búa lớn" cho việc điều phối nhiều agent (Multi-agent). Phù hợp để scale nhanh workflow mà không cần cấu hình phức tạp.

* **Cài đặt:**
```bash
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode

```


* **Cách sử dụng:** * Chạy `/oh-my-claudecode:omc-setup` để bắt đầu.
* Sử dụng các chế độ như `Autopilot` (tự trị) hoặc `Swarm` (phối hợp nhóm agent).



---

## 🚀 Các công cụ đang Trending (Advanced)

| Công cụ | Loại hình | Công dụng chính |
| --- | --- | --- |
| **Model Context Protocol (MCP)** | Giao thức | "Cổng kết nối" vạn năng giúp Claude Code đọc Database, Google Drive, hay Slack an toàn. |
| **claude-flow (ruvnet)** | Orchestration | **Cài đặt:** `npm install -g claude-flow@alpha`. Dùng để tạo các "hive-mind" (tổ hợp trí tuệ) giải quyết task siêu khó. |
| **Serena** | MCP Server | Giúp Claude hiểu sâu codebase và thực thi lệnh có kiểm soát, tránh việc AI "quậy phá" lung tung. |
| **claude-scientific-skills** | Domain Skills | **Cài đặt:** `/plugin marketplace add K-Dense-AI/claude-scientific-skills`. Cung cấp 140+ kỹ năng phân tích y sinh, hóa học và dữ liệu. |

---

## 💡 Kết luận: Cách build "AI Developer Stack" của bạn

Để đạt hiệu suất tối đa, đừng chỉ dùng Claude Code "vã". Hãy kết hợp theo công thức sau:

1. **Nền tảng:** Cài **Superpowers** để có quy trình chuẩn.
2. **Trí nhớ:** Cài **claude-mem** để không bao giờ phải giải thích lại từ đầu.
3. **Công cụ:** Cài các plugin từ **wshobson** hoặc **scientific-skills** tùy theo ngôn ngữ bạn đang viết.
4. **Kết nối:** Sử dụng **MCP** để AI có thể truy cập dữ liệu thực tế (thay vì chỉ đọc file code).

**Bước tiếp theo bạn nên làm:** Bạn có muốn tôi hướng dẫn cấu hình một **MCP Server** cụ thể (như kết nối với GitHub hay Database) để dùng cùng với các plugin này không?
