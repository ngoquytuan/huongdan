Để xóa sạch thư viện Python và cài đặt lại trên Windows, có thể làm theo các bước sau:

### Bước 1: Gỡ cài đặt Python

1. **Mở Control Panel**:
   - Nhấn `Windows + R`, gõ `control` và nhấn `Enter`.
2. **Chọn "Programs"**:
   - Click vào "Programs" rồi chọn "Programs and Features".
3. **Tìm Python**:
   - Tìm Python trong danh sách các chương trình đã cài đặt.
4. **Gỡ cài đặt**:
   - Click chuột phải vào Python và chọn "Uninstall". Làm theo hướng dẫn để hoàn tất quá trình gỡ cài đặt.

### Bước 2: Xóa các thư viện Python

1. **Xóa thư mục cài đặt**:
   - Mở File Explorer và điều hướng đến thư mục cài đặt Python (thường là `C:\Users\<YourUsername>\AppData\Local\Programs\Python\PythonXX`, với `XX` là phiên bản Python).
2. **Xóa thư mục**:
   - Xóa toàn bộ thư mục này.
3. **Xóa các thư viện đã cài đặt**:
   - Nếu bạn đã cài đặt pip, kiểm tra thư mục `C:\Users\<YourUsername>\AppData\Roaming\Python` và xóa các thư mục liên quan.

### Bước 3: Cài đặt lại Python

1. **Tải Python**:
   - Truy cập trang web chính thức [python.org](http://python.org) và tải phiên bản mới nhất.
2. **Cài đặt**:
   - Chạy tệp cài đặt và đảm bảo chọn tùy chọn "Add Python to PATH". Sau đó, làm theo hướng dẫn để hoàn tất cài đặt.

### Bước 4: Kiểm tra cài đặt

1. **Mở Command Prompt**:
   - Nhấn `Windows + R`, gõ `cmd` và nhấn `Enter`.
2. **Kiểm tra phiên bản Python**:
   - Gõ `python --version` để kiểm tra xem Python đã được cài đặt thành công hay chưa.
3. **Kiểm tra pip**:
   - Gõ `pip --version` để kiểm tra xem pip đã được cài đặt hay chưa.

Đúng rồi anh 👍, vấn đề là `underthesea` hiện tại chưa tương thích tốt với Python mới (3.13.x). Nó thường ổn định nhất ở Python **3.8 → 3.10** (3.11 đôi khi cũng chạy được).  
 Giải pháp: Tạo một môi trường ảo riêng trên Windows với phiên bản Python cũ hơn, rồi cài `underthesea` và các dependency cần thiết.

Em hướng dẫn chi tiết nhé:

---

## 🔹 Bước 1: Tải Python phù hợp

- Vào trang [Python Releases](https://www.python.org/downloads/release/python-31011/)
- Tải **Python 3.10.11 (Windows x64)** → đây là phiên bản ổn định với `underthesea`.
- Khi cài nhớ tick **Add to PATH**.

---

## 🔹 Bước 2: Tạo môi trường ảo

Mở **Command Prompt (cmd)** hoặc **PowerShell**, gõ:

```bash
# Tạo folder dự án
mkdir vietnamese_nlp
cd vietnamese_nlp

# Tạo môi trường ảo với python 3.10
py -3.10 -m venv venv

# Kích hoạt môi trường ảo
venv\Scripts\activate
```

Khi thành công, dòng lệnh sẽ có `(venv)` phía trước.

---

## 🔹 Bước 3: Cài đặt underthesea

Trong môi trường ảo, chạy:

```bash
pip install --upgrade pip wheel setuptools
pip install underthesea
```

Nếu cần thêm tính năng nâng cao (POS tagging, dependency parsing), cài thêm:

```bash
pip install underthesea[deep]
```

---

## 🔹 Bước 4: Kiểm thử nhanh

Tạo file `test_underthesea.py`:

```python
from underthesea import word_tokenize

text = "Xin chào, tôi đang học xử lý ngôn ngữ tự nhiên tiếng Việt."
tokens = word_tokenize(text)
print(tokens)
```

Chạy thử:

```bash
python test_underthesea.py
```

Nếu in ra danh sách token (phân tách từ đúng tiếng Việt) → thành công ✅.

---

## 🔹 Bước 5: Nếu vẫn lỗi

- Một số dependency (`pyvi`, `scipy`, `numpy`) đôi khi bị lỗi build. Giải pháp: cài bản wheel có sẵn:

```bash
pip install numpy==1.23.5 scipy==1.10.1
```

Rồi cài lại:

```bash
pip install underthesea
```

---

👉 Em có thể viết cho anh một file **install script** (`setup_env.bat`) để chỉ cần click là tạo môi trường và cài `underthesea` tự động.

Anh có muốn em viết luôn file `setup_env.bat` đó để anh chỉ cần double-click chạy không?

À, lỗi này là do **PowerShell Execution Policy** chặn không cho chạy script (`Activate.ps1`). Đây là vấn đề thường gặp trên Windows khi kích hoạt virtualenv bằng PowerShell.

Có 3 cách xử lý:

---

## 🔹 Cách 1: Dùng `activate.bat` thay vì `Activate.ps1`

Trong Windows, mỗi môi trường ảo có sẵn file `.bat` cho CMD, anh thử chạy:

```powershell
venvAAA\Scripts\activate.bat
```

Nó sẽ mở trong CMD-style activation, chạy được luôn.

---

## 🔹 Cách 2: Tạm thời cho phép chạy script trong PowerShell

Nếu muốn dùng PowerShell, chạy lệnh này (chỉ cho phiên này, không ảnh hưởng toàn hệ thống):

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

Sau đó chạy lại:

```powershell
.\venvAAA\Scripts\Activate.ps1
```

---

## 🔹 Cách 3: Cho phép vĩnh viễn (ít khuyên dùng)

Nếu anh muốn khỏi phải gõ lại mỗi lần, có thể cho phép với scope CurrentUser:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

👉 Em khuyên: Nếu anh chỉ tập trung Python, thì dùng **Cách 1 (**`activate.bat`**)** cho nhanh gọn, không cần đụng tới ExecutionPolicy.

---

Anh muốn em viết luôn file `setup_env.bat` (chạy một lần là tạo venv + cài underthesea) hay anh muốn từng bước thủ công cho dễ kiểm soát?