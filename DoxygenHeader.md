Để nhận được mã nguồn C cho hệ thống nhúng (Embedded) đạt chuẩn chuyên nghiệp, bạn cần một Prompt yêu cầu cụ thể về **cấu trúc (structure)**, **tài liệu (documentation)** và **quy ước đặt tên (naming conventions)**.

Dưới đây là một mẫu Prompt tiếng Anh tối ưu mà bạn có thể sử dụng:

---

### Prompt Tiếng Anh (Copy & Paste)

> **Role:** Act as a Senior Embedded Systems Engineer with expertise in C programming for microcontrollers (MCU).
> **Task:** Write a C source code for [TÊN TÍNH NĂNG/MODULE, ví dụ: an I2C driver for an OLED display].
> **Requirements for Professional Code:**
> 1. **Doxygen Header:** Every file must start with a comprehensive Doxygen-style header including `@file`, `@author`, `@brief`, `@version`, `@date`, and a short `Changelog`.
> 2. **Coding Standards:** Follow a strict naming convention (e.g., `snake_case` for functions/variables, `UPPER_CASE` for macros). Use `stdint.h` types (e.g., `uint8_t`, `int32_t`) for hardware portability.
> 3. **Documentation:** Provide Doxygen comments for every function using `@param` for inputs and `@return` for output descriptions.
> 4. **Error Handling:** Implement robust error checking (e.g., return `enum` status codes instead of magic numbers).
> 5. **Structure:** Organize the code into:
> * Includes
> * Private Defines/Macros
> * Private Typedefs (Structs/Enums)
> * Private Function Prototypes (Static)
> * Public Function Implementations
> * Private Function Implementations
> 
> 
> 6. **Clarity:** Write clean, modular, and non-blocking code. Explain the "Why" behind complex logic using inline comments.
> 
> 
> **MCU Target:** [TÊN MCU, ví dụ: STM32F4 or ESP32]

---

### Giải thích các điểm mấu chốt trong Prompt:

* **Senior Embedded Systems Engineer:** Thiết lập vai trò chuyên gia để LLM ưu tiên tính hiệu quả của bộ nhớ và hiệu suất phần cứng.
* **Doxygen-style header:** Yêu cầu định dạng mô tả đầu file như chúng ta đã thảo luận.
* **stdint.h types:** Đây là dấu hiệu của lập trình nhúng chuyên nghiệp. Thay vì dùng `int` (có độ dài thay đổi tùy chip), ta dùng `uint8_t`, `uint32_t` để đảm bảo độ chính xác trên mọi MCU.
* **Error Handling (Enum):** Yêu cầu trả về các trạng thái như `ERR_OK`, `ERR_TIMEOUT` thay vì các con số 0, 1 khó hiểu.
* **Non-blocking code:** Rất quan trọng trong hệ thống nhúng để chương trình không bị "treo" khi chờ đợi phần cứng.

---

### Mẹo nhỏ:

Nếu bạn đang dùng **VS Code**, sau khi LLM tạo ra code, bạn có thể cài thêm extension **"Clang-Format"** và nhấn `Shift + Alt + F`. Nó sẽ tự động căn chỉnh code của LLM theo chuẩn công nghiệp (như chuẩn của Google hay LLVM) giúp file của bạn trông hoàn hảo hơn nữa.

Bạn có muốn tôi thử áp dụng Prompt này để viết một module cụ thể nào đó (ví dụ: điều khiển LED Blink hoặc đọc cảm biến) để bạn xem thử kết quả không?
