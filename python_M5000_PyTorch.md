The issue is that your GPU, the NVIDIA Quadro M5000, has a CUDA capability of 5.2, which is not supported by the installed PyTorch version (2.8.0+cu126). PyTorch 2.8.0 requires a minimum CUDA capability of 6.1. To resolve this, you need to install a PyTorch version that supports CUDA capability 5.2, such as PyTorch 1.13.1 with CUDA 11.6, and ensure compatibility with your Python environment and other packages.

Here’s a step-by-step guide to reinstall PyTorch and related dependencies:

### Step 1: Uninstall the Current PyTorch Version
1. Open a Command Prompt or PowerShell as Administrator.
2. Uninstall the current PyTorch package:
   ```bash
   pip uninstall torch torchvision torchaudio
   ```
   Confirm the uninstallation by pressing `y` when prompted.

### Step 2: Verify Your Python Environment
- Your Python version is 3.10, which is compatible with PyTorch 1.13.1. Ensure you’re working in the correct Python environment (e.g., a virtual environment if you’re using one):
  ```bash
  python --version
  ```
- If you’re using a virtual environment, activate it:
  ```bash
  C:\path\to\your\venv\Scripts\activate
  ```

### Step 3: Install a Compatible PyTorch Version
- PyTorch 1.13.1 with CUDA 11.6 supports CUDA capability 5.2. Install it using the following command:
  ```bash
  pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
  ```
- This command specifies PyTorch 1.13.1 with CUDA 11.6, which is compatible with your Quadro M5000.

### Step 4: Verify PyTorch Installation
- After installation, verify that PyTorch recognizes your GPU:
  ```python
  python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
  ```
- Expected output should look like:
  ```
  1.13.1+cu116
  True
  Quadro M5000
  ```
- If CUDA is available and the GPU is detected, the installation is successful.

### Step 5: Check Compatibility of Other Packages
Your current packages (`huggingface_hub`, `transformers`, `sentence-transformers`, `chromadb`) may have dependencies on newer PyTorch versions. Since you’re downgrading to PyTorch 1.13.1, you may need to adjust these packages to compatible versions:

1. **huggingface_hub**: Version 0.17.3 should work, but if issues arise, try:
   ```bash
   pip install huggingface_hub==0.16.4
   ```
2. **transformers**: Version 4.35.2 may require a newer PyTorch. Install a compatible version (e.g., 4.25.1):
   ```bash
   pip install transformers==4.25.1
   ```
3. **sentence-transformers**: Version 2.2.2 should be compatible, but if errors occur, try:
   ```bash
   pip install sentence-transformers==2.2.0
   ```
4. **chromadb**: Version 1.0.0 may have issues. Install a slightly older version if needed:
   ```bash
   pip install chromadb==0.4.24
   ```

- After installing, verify compatibility by running your application or a test script that uses these libraries.

### Step 6: Test Your Application
- Run your application or a test script to ensure everything works with the GPU:
  ```python
  import torch
  from transformers import pipeline

  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  print(f"Using device: {device}")
  # Example with transformers
  nlp = pipeline("sentiment-analysis", device=0 if torch.cuda.is_available() else -1)
  print(nlp("This is a test sentence"))
  ```
- If the script runs without CUDA-related errors and uses the GPU, the setup is correct.

### Additional Notes
- **NVIDIA Driver**: Your NVIDIA driver version (572.16) supports CUDA 11.6, so no driver update is needed.
- **CUDA Toolkit**: You don’t need to install the CUDA Toolkit separately, as PyTorch includes the necessary CUDA libraries.
- **Virtual Environment**: Using a virtual environment is recommended to avoid conflicts with other projects:
  ```bash
  python -m venv myenv
  myenv\Scripts\activate
  ```
- **If Issues Persist**:
  - Ensure no conflicting CUDA versions are installed.
  - Check for errors in your application logs and address specific package incompatibilities.
  - Visit https://pytorch.org/get-started/previous-versions/ for other compatible PyTorch versions if needed.

If you encounter specific errors during this process, share them, and I can provide further assistance.


---

Rồi, mình hiểu hệ thống bạn rồi 👍.
Bạn đang chạy trên **GPU Quadro M5000 (CUDA 11.6)** với **PyTorch 1.13.1+cu116**, nên bộ thư viện phải đồng bộ về phiên bản cũ (không thể lên PyTorch 2.x).

Dựa trên script `evaluate2.py` và các lỗi bạn gặp, mình tạo cho bạn file `requirements.txt` **ổn định nhất** để chạy được với M5000:

---

### 📄 requirements.txt

```txt
# Core deep learning
torch==1.13.1+cu116
torchvision==0.14.1+cu116
torchaudio==0.13.1+cu116
--extra-index-url https://download.pytorch.org/whl/cu116

# Sentence embeddings
sentence-transformers==2.2.2
transformers==4.30.2
huggingface_hub==0.13.4
tokenizers==0.13.3

# Data & processing
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Vietnamese NLP
pyvi>=0.1.1
# underthesea>=6.7.0   # tùy chọn nếu muốn thêm tokenizer khác

# Utilities
accelerate==0.20.3
pathlib
```

---

### 🔧 Cách dùng

1. Lưu file trên vào `requirements.txt`.
2. Cài bằng:

   ```bash
   pip install -r requirements.txt
   ```
3. Kiểm tra lại PyTorch có nhận GPU:

   ```bash
   python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
   ```

   Bạn sẽ thấy:

   ```
   1.13.1+cu116 True Quadro M5000
   ```

---

👉 Bộ này đảm bảo:

* `sentence-transformers==2.2.2` dùng được với PyTorch 1.13.
* `transformers==4.30.2` không đòi `torch>=2.x`.
* `huggingface_hub==0.13.4` giữ lại `cached_download` (bắt buộc cho sentence-transformers cũ).

---

Bạn có muốn mình gói luôn thành **environment.yml** (cho Conda) để bạn tạo môi trường ảo sạch sẽ, tránh xung đột pip không?


Mình thấy ngay vấn đề 👇

Bạn đã **hạ `huggingface_hub` xuống 0.13.4** để giữ lại `cached_download` (đúng), nhưng lúc này `accelerate` + `transformers` lại đòi một hàm **mới** trong `huggingface_hub` (`split_torch_state_dict_into_shards`), hàm này chỉ có trong **huggingface_hub >= 0.14.0**.

➡️ Tóm gọn:

* `sentence-transformers==2.2.2` cần `cached_download` (chỉ có ở `huggingface_hub<=0.13.4`)
* `transformers 4.30.2` + `accelerate` lại đòi `split_torch_state_dict_into_shards` (chỉ có ở `huggingface_hub>=0.14`)

Hai yêu cầu này **xung đột nhau**.

---

### ✅ Cách giải quyết

Có 2 hướng:

#### 🔹 Cách 1 (ổn định, khuyên dùng):

Hạ cả `transformers` và `accelerate` xuống **phiên bản cùng thời** với `sentence-transformers 2.2.2` (giữa năm 2022).
Ví dụ:

```bash
pip install transformers==4.27.4 sentence-transformers==2.2.2 huggingface_hub==0.13.4 accelerate==0.17.1
```

Bộ này chạy ổn với **PyTorch 1.13.1** và GPU M5000.

---

#### 🔹 Cách 2 (mới hơn, khó hơn):

* Giữ `huggingface_hub` >=0.14 để có `split_torch_state_dict_into_shards`.
* Nhưng phải vá code của `sentence-transformers` (bỏ `cached_download`, thay bằng `hf_hub_download`).

Cách này cần sửa code trong site-packages, hơi phiền.

---

### 📌 Đề xuất cho bạn

Với GPU cũ và PyTorch 1.13, mình khuyên dùng **Cách 1**:

**requirements.txt (bản fix cuối cùng cho bạn):**

```txt
torch==1.13.1+cu116
torchvision==0.14.1+cu116
torchaudio==0.13.1+cu116
--extra-index-url https://download.pytorch.org/whl/cu116

sentence-transformers==2.2.2
transformers==4.27.4
huggingface_hub==0.13.4
tokenizers==0.13.3
accelerate==0.17.1

numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

matplotlib>=3.7.0
seaborn>=0.12.0

pyvi>=0.1.1
pathlib
```

---

👉 Hỏi nhanh: bạn muốn mình viết sẵn lệnh **gỡ sạch thư viện cũ** (uninstall hết rồi cài lại đúng bộ này) để chắc chắn không xung đột nữa không?

