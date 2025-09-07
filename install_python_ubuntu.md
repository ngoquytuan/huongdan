Ok, mình soạn sẵn cho bạn một script `setup-python311.sh` để chạy một lần là có Python 3.11 + pip riêng, không đụng pip hệ thống, cuối cùng tự kiểm tra version luôn.

---

### 📄 `setup-python311.sh`

```bash
#!/bin/bash
set -e

echo "🔹 Cập nhật hệ thống và thêm PPA deadsnakes..."
sudo apt update
sudo apt install -y software-properties-common curl
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

echo "🔹 Cài Python 3.11 và các gói cần thiết..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

echo "🔹 Kích hoạt pip cho Python 3.11..."
python3.11 -m ensurepip --upgrade
python3.11 -m pip install --upgrade pip

echo "🔹 Cấu hình update-alternatives để chọn Python mặc định..."
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2

echo "✅ Hoàn tất cài đặt!"
echo
echo "🔎 Kiểm tra phiên bản Python và pip:"
python3.11 --version
python3.11 -m pip --version
python3 --version
```

---

### 🚀 Cách dùng

1. Lưu file:

   ```bash
   nano setup-python311.sh
   ```

   Dán nội dung vào, lưu lại (`Ctrl+O`, `Enter`, `Ctrl+X`).

2. Cấp quyền chạy:

   ```bash
   chmod +x setup-python311.sh
   ```

3. Chạy script:

   ```bash
   ./setup-python311.sh
   ```

---

👉 Sau khi chạy xong, bạn có thể chọn mặc định `python3` trỏ về 3.11 bằng:

```bash
sudo update-alternatives --config python3
```

---

Bạn muốn mình bổ sung thêm bước **tự động chọn luôn Python 3.11 làm mặc định** trong script, hay để bạn chọn thủ công cho chắc?
---
Hiểu rồi 👍. Trường hợp này khá hay gặp khi bạn cài thêm Python version mới (3.11/3.12) rồi thay đổi `update-alternatives`. Một số ứng dụng **GNOME Terminal** trên Ubuntu phụ thuộc vào Python của hệ thống (`/usr/bin/python3`). Nếu `python3` trỏ sai version hoặc thiếu module hệ thống (`apt_pkg`, `gi`...), terminal GUI sẽ **không mở được**.

---

### 🔎 Nguyên nhân khả dĩ

* Bạn đã set `python3` mặc định sang 3.11, nhưng các gói của Ubuntu (terminal, command-not-found, gnome-shell...) lại được build cho Python 3.12 → crash.
* Vì vậy khi click icon Terminal, nó không chạy.

SSH vẫn hoạt động vì bạn dùng `bash` chứ không cần Python để render GUI.

---

### 🛠️ Cách khắc phục

#### 1. Khôi phục lại `python3` mặc định về 3.12 (cho hệ thống)

Chạy trên SSH:

```bash
sudo update-alternatives --config python3
```

Chọn đường dẫn `/usr/bin/python3.12`.

---

#### 2. Cài lại gói cần thiết (nếu vẫn lỗi)

```bash
sudo apt install --reinstall gnome-terminal python3-apt -y
```

---

#### 3. Đảm bảo vẫn dùng được Python 3.11 cho dự án

Không cần xoá 3.11, bạn chỉ cần gọi trực tiếp:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

Hoặc nếu muốn, alias riêng:

```bash
echo 'alias py311="python3.11"' >> ~/.bashrc
source ~/.bashrc
```

---

✅ Sau bước (1) + (2), Terminal GUI trên Ubuntu sẽ mở lại bình thường, còn dự án của bạn vẫn chạy với Python 3.11 trong venv.

---

Bạn có muốn mình viết cho bạn một đoạn script `fix-terminal.sh` (chạy qua SSH) để tự động đưa `python3` về 3.12 + reinstall gnome-terminal, khỏi cần làm tay từng bước không?

