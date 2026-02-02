Với bộ công cụ cực kỳ mạnh mẽ mà bạn đã cài đặt, việc kiểm tra lỗi tiềm ẩn không chỉ dừng lại ở quét cú pháp mà còn đi sâu vào logic và kiến trúc. Dưới đây là những plugin và skill "đắt giá" nhất bạn nên dùng để truy tìm lỗi, kèm theo các prompt thực chiến.

## 1. Các Plugin ưu tiên hàng đầu

### **`codebase-cleanup` & `python-development` (Cặp đôi kiểm soát chất lượng)**

* **Công dụng:** `codebase-cleanup` giúp phát hiện các "mùi code" (code smells), code thừa, hoặc cấu trúc lộn xộn. Trong khi đó, agent `python-pro` trong `python-development` có kiến thức chuyên sâu về các lỗi runtime đặc thù của Python và Pydantic.
* **Skill tiêu biểu:** `linting`, `performance-optimization`.

### **`superpowers` (Kỹ năng Debug hệ thống)**

* **Công dụng:** Sử dụng quy trình `systematic-debugging` gồm 4 giai đoạn để tìm nguyên nhân gốc rễ (root cause) thay vì chỉ sửa phần ngọn.
* **Skill tiêu biểu:** `systematic-debugging` (bao gồm root-cause-tracing và defense-in-depth).

### **`claude-mem` (Kiểm tra sự nhất quán)**

* **Công dụng:** Rất quan trọng để kiểm tra xem code hiện tại có đang "đi ngược" lại với các logic hoặc bản sửa lỗi mà bạn đã thực hiện trong quá khứ không.
* **Skill tiêu biểu:** `mem-search`.

---

## 2. Các Prompt ví dụ theo từng kịch bản

### **Kịch bản 1: Quét lỗi tổng thể và rà soát Pydantic V2**

Sử dụng khi bạn vừa viết xong một module và muốn đảm bảo nó "sạch".

> **Prompt:** "Sử dụng agent `python-pro` từ `python-development` kết hợp với `codebase-cleanup` để thực hiện một đợt audit chuyên sâu trên module X. Hãy tìm các lỗi tiềm ẩn về:
> 1. Type safety và các trường metadata chưa được validate bằng Pydantic V2.
> 2. Các điểm có thể gây lỗi 'Silent failure' (nuốt ngoại lệ mà không log).
> 3. Kiểm tra tính nhất quán với các hướng dẫn trong file `Claude.md`."
> 
> 

### **Kịch bản 2: Tìm lỗi logic dựa trên lịch sử dự án**

Sử dụng khi bạn nghi ngờ code mới có thể gây lỗi cho các tính năng cũ (Regression bug).

> **Prompt:** "Sử dụng `claude-mem` để tra cứu các lỗi liên quan đến [tên tính năng, ví dụ: Retrieval logic] đã từng xảy ra. Sau đó, dùng skill `systematic-debugging` từ `superpowers` để đối chiếu với đoạn code hiện tại xem liệu chúng ta có đang lặp lại sai lầm cũ hoặc tạo ra lỗ hổng bảo mật nào không."

### **Kịch bản 3: Kiểm tra khả năng chịu tải và Edge Cases**

Sử dụng `unit-testing` để tạo ra các tình huống "ngặt nghèo".

> **Prompt:** "Sử dụng plugin `unit-testing` và `tdd-workflows` để tạo ra các test cases cực hạn (edge cases) cho hàm xử lý RAG này. Hãy tập trung vào việc truyền dữ liệu đầu vào bị thiếu, sai định dạng, hoặc văn bản tiếng Việt có ký tự đặc biệt để xem code có crash không."

---

## 3. Lời khuyên về quy trình (Workflow)

Để đạt hiệu quả cao nhất, bạn nên áp dụng quy trình **"Audit - Test - Memory"**:

1. **Audit:** Dùng `python-pro` để soi lỗi kỹ thuật.
2. **Test:** Dùng `unit-testing` để chạy thử các kịch bản lỗi.
3. **Memory:** Dùng `claude-mem` để đảm bảo lỗi đó được ghi nhớ và không tái diễn.

**Lưu ý về lỗi Bun:** Vì bạn đang gặp lỗi Bun kẹt, hãy chắc chắn đã chạy lệnh `kill $(lsof -t -i:37777)` trước khi dùng các prompt có liên quan đến `claude-mem` để AI có thể truy xuất dữ liệu quá khứ một cách ổn định nhất.

**Bạn có muốn tôi thử thực hiện một lệnh quét lỗi (Audit) thực tế cho một file cụ thể nào trong dự án của bạn không?**
