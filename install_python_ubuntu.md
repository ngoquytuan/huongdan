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
