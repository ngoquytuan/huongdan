Lỗi bạn gặp là:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>
```

### 💡 Nguyên nhân

Khi Python ghi file (`f.write(...)`), hệ thống dùng **mã hóa mặc định của Windows (`cp1252`)**.
Ký tự `✅` (mã Unicode `\u2705`) **không nằm trong bảng mã cp1252**, nên Python không thể mã hóa được và báo lỗi.

---

### ✅ Cách khắc phục

#### **Cách 1 – Ghi file với encoding UTF-8**

Thêm `encoding="utf-8"` khi mở file:

```python
with open("report.txt", "w", encoding="utf-8") as f:
    f.write("✅ No sharing detected\n")
```

👉 Đây là cách tốt nhất — UTF-8 hỗ trợ mọi ký tự Unicode (emoji, ký tự đặc biệt, v.v.).

---

#### **Cách 2 – Loại bỏ hoặc thay emoji**

Nếu bạn không cần emoji:

```python
f.write("No sharing detected\n")
```

---

#### **Cách 3 – Đặt mã hóa mặc định toàn cục (ít khuyến nghị)**

Thêm vào đầu file Python:

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

*(chỉ hữu ích nếu bạn in ra console, không phải ghi file).*

---

### 🔍 Tóm tắt

| Nguyên nhân                            | Cách sửa                            |
| -------------------------------------- | ----------------------------------- |
| Windows dùng cp1252 không hỗ trợ emoji | Dùng `encoding="utf-8"` khi mở file |

---

Nếu bạn gửi mình **đoạn code mở file** (`with open(...) as f:`), mình có thể chỉ rõ bạn cần chỉnh dòng nào. Bạn có muốn mình chỉ ra cụ thể trong hàm `generate_final_report` không?
