Để nâng cấp tính năng hoặc lên đời thư viện (như Pydantic V2) một cách bài bản, bạn nên kết hợp các plugin theo một **quy trình 4 giai đoạn**. Việc sử dụng rời rạc các plugin sẽ không phát huy hết sức mạnh của chúng.

Dưới đây là công thức phối hợp các plugin bạn đã cài và các prompt ví dụ cụ thể:

---

### 1. Giai đoạn Lập kế hoạch (Planning & Context)

Trước khi gõ code, bạn cần AI hiểu rõ "di sản" (legacy code) và mục tiêu mới.

* **Plugin ưu tiên:** `planning-with-files`, `context-management`, `claude-mem`.
* **Mục tiêu:** Tạo ra một bản thiết kế (Design Doc) và kế hoạch thực thi để không bị lạc hướng.

> **Prompt ví dụ:**
> "Sử dụng `context-management` để quét toàn bộ module RAG hiện tại và `claude-mem` để tóm tắt các quyết định kiến trúc trước đây. Sau đó, dùng `planning-with-files` để tạo file `migration_plan.md` cho việc nâng cấp lên Pydantic V2. Kế hoạch phải chia nhỏ thành các tác vụ 5 phút và lưu ý không làm hỏng các hàm trích xuất tiếng Việt hiện có."

---

### 2. Giai đoạn Dọn dẹp & Chuẩn bị (Cleanup & Refactor)

Làm sạch "rác" để việc nâng cấp diễn ra trên một nền tảng gọn gàng.

* **Plugin ưu tiên:** `codebase-cleanup`, `code-refactoring`.
* **Mục tiêu:** Loại bỏ code thừa và chuẩn hóa định dạng trước khi áp dụng logic mới.

> **Prompt ví dụ:**
> "Chạy `codebase-cleanup` để tìm các file obsolete (đã cũ) và di chuyển chúng vào thư mục `nous/`. Sau đó, sử dụng `code-refactoring` để chuẩn hóa các docstring trong `src/utils/` theo chuẩn Google Style trước khi chúng ta thực hiện nâng cấp thư viện."

---

### 3. Giai đoạn Thực thi Kỷ luật (Implementation)

Sử dụng phương pháp "siêu năng lực" để viết code chất lượng cao.

* **Plugin ưu tiên:** `superpowers`, `python-development`, `tdd-workflows`.
* **Mục tiêu:** Viết code có test bảo vệ, tuân thủ đúng quy trình TDD (Test-Driven Development).

> **Prompt ví dụ:**
> "Kích hoạt `superpowers` và sử dụng chuyên gia từ `python-development` để thực hiện tác vụ số 3 trong kế hoạch. Hãy áp dụng `tdd-workflows`: viết unit test cho Model Pydantic mới trước, đảm bảo nó bắt được lỗi khi `quality_score > 1.0`, sau đó mới viết code triển khai chính thức."

---

### 4. Giai đoạn Điều phối & Bàn giao (Orchestration & Docs)

Khi dự án lớn dần, bạn cần sự phối hợp đa tác nhân.

* **Plugin ưu tiên:** `full-stack-orchestration`, `backend-development`, `llm-application-dev`.
* **Mục tiêu:** Đảm bảo tính năng mới tương thích tốt với toàn bộ hệ thống (Backend, Vector DB, LLM).

> **Prompt ví dụ:**
> "Sử dụng `full-stack-orchestration` để điều phối một đợt kiểm tra cuối cùng. Gọi `backend-development` để review lại API design và `llm-application-dev` để đánh giá lại hiệu quả của RAG retrieval sau khi đã nâng cấp Pydantic. Cuối cùng, cập nhật file `handover.md` với các thay đổi mới nhất."

---

### 💡 Bảng tóm tắt nhanh "Vũ khí" theo tình huống

| Khi bạn muốn... | Hãy dùng tổ hợp Plugin này |
| --- | --- |
| **Sửa lỗi khó** | `superpowers` + `python-development` (skill: systematic-debugging) |
| **Thêm API mới** | `backend-development` + `planning-with-files` |
| **Nâng cấp thư viện** | `code-refactoring` + `tdd-workflows` |
| **Tối ưu hóa RAG** | `llm-application-dev` + `claude-mem` |

---

**Lời khuyên:** Bạn nên bắt đầu bằng cách yêu cầu Claude tạo kế hoạch trước (`planning-with-files`). Việc có một file `.md` ghi lại kế hoạch trong chính folder dự án sẽ giúp Claude giữ được sự ổn định tuyệt vời khi thực hiện các tác vụ phức tạp.

**Bạn có muốn tôi thử viết một prompt "tổng lực" để thực hiện bước đầu tiên trong việc refactor file `app.py` khổng lồ của bạn không?**
