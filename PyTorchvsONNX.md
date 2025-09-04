Rõ rồi 👍 Em sẽ soạn cho anh một **tài liệu đầy đủ** (kiểu hướng dẫn kỹ thuật) để anh hoặc đồng nghiệp có thể chạy lại toàn bộ quá trình **so sánh PyTorch vs ONNX Runtime**.

---

# 📘 Hướng dẫn: So sánh tốc độ Inference giữa PyTorch và ONNX Runtime

## 1️⃣ Giới thiệu

Trong các hệ thống AI/ML thực tế, PyTorch thường được dùng trong **quá trình huấn luyện** và tinh chỉnh mô hình. Tuy nhiên khi triển khai (deployment), ta cần tốc độ inference cao và gọn nhẹ → ONNX Runtime là lựa chọn tối ưu.

Tài liệu này hướng dẫn:

* Cài đặt các thư viện cần thiết.
* Viết script benchmark một mô hình sentence embedding (`paraphrase-multilingual-MiniLM-L12-v2`).
* So sánh tốc độ inference giữa PyTorch và ONNX Runtime.

---

## 2️⃣ Cài đặt môi trường

Yêu cầu: Python 3.9+ (nên dùng Python 3.10).

```bash
# Tạo virtualenv (khuyến nghị)
python -m venv venvONNX
.\venvONNX\Scripts\activate   # Windows
source venvONNX/bin/activate # Linux/Mac

# Cài đặt thư viện cần thiết
pip install torch==2.2.2
pip install sentence-transformers
pip install transformers
pip install onnx onnxruntime
```

Kiểm tra lại:

```bash
python -c "import torch, onnxruntime; print(torch.__version__, onnxruntime.__version__)"
```

---

## 3️⃣ Script so sánh (PyTorchvsONNXRuntime.py)

Lưu file dưới tên `PyTorchvsONNXRuntime.py`:

```python
import time
import torch
import onnx
import onnxruntime as ort
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

# ----------- Config ------------
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
onnx_path = "model.onnx"

sentences = [
    "Xin chào, tôi là AI.",
    "Hôm nay trời đẹp quá.",
    "Tôi thích học máy."
]

# ----------- PyTorch Inference ------------
model_torch = SentenceTransformer(model_name)
start = time.time()
embeddings_torch = model_torch.encode(sentences, convert_to_numpy=True)
end = time.time()

print("🔹 PyTorch Inference")
print("Embeddings shape (PyTorch):", embeddings_torch.shape)
print(f"Time (PyTorch): {end - start:.4f} s")

# ----------- Export ONNX nếu chưa có ------------
tokenizer = AutoTokenizer.from_pretrained(model_name)
try:
    onnx_model = onnx.load(onnx_path)
    print("⚡ Dùng lại ONNX model đã có:", onnx_path)
except:
    print("⚡ Exporting model sang ONNX...")
    model_onnx = model_torch._first_module().auto_model.cpu()
    dummy_input = tokenizer("Câu thử nghiệm", return_tensors="pt")
    dummy_input = {
        "input_ids": dummy_input["input_ids"].cpu(),
        "attention_mask": dummy_input["attention_mask"].cpu()
    }
    torch.onnx.export(
        model_onnx,
        (dummy_input["input_ids"], dummy_input["attention_mask"]),
        onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "last_hidden_state": {0: "batch", 1: "sequence"}
        },
        opset_version=14
    )
    print("✅ Xuất ONNX thành công:", onnx_path)

# ----------- ONNX Inference ------------
ort_session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

tokens = tokenizer(sentences, padding=True, truncation=True, return_tensors="np")
start = time.time()
onnx_outputs = ort_session.run(
    ["last_hidden_state"],
    {"input_ids": tokens["input_ids"], "attention_mask": tokens["attention_mask"]}
)
end = time.time()

embeddings_onnx = onnx_outputs[0].mean(axis=1)  # pooling
print("\n🔹 ONNX Inference")
print("Embeddings shape (ONNX):", embeddings_onnx.shape)
print(f"Time (ONNX): {end - start:.4f} s")
```

---
```python
import time
import torch
import onnx
import onnxruntime as ort
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

# ======================
# 1. Chuẩn bị model và tokenizer
# ======================
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model_torch = SentenceTransformer(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

sentences = [
    "Xin chào, tôi đang thử benchmark.",
    "PyTorch và ONNX khác nhau thế nào?",
    "Chúng ta sẽ đo tốc độ inference."
]

# ======================
# 2. PyTorch Inference
# ======================
print("🔹 PyTorch Inference")
start = time.time()
embeddings_torch = model_torch.encode(sentences)
end = time.time()
print("Embeddings shape (PyTorch):", embeddings_torch.shape)
print("Time (PyTorch): %.4f s" % (end - start))

# ======================
# 3. Export sang ONNX
# ======================
onnx_path = "model.onnx"

try:
    onnx_model = onnx.load(onnx_path)
    print(f"⚡ Dùng lại ONNX model đã có: {onnx_path}")
except:
    print("⚡ Exporting model sang ONNX...")
    # Lấy backbone từ SentenceTransformer và đưa về CPU
    model_onnx = model_torch._first_module().auto_model.cpu()

    # Dummy input cũng phải ở CPU
    dummy_input = tokenizer("Câu thử nghiệm", return_tensors="pt")
    dummy_input = {
        "input_ids": dummy_input["input_ids"].cpu(),
        "attention_mask": dummy_input["attention_mask"].cpu()
    }

    # Export
    torch.onnx.export(
        model_onnx,
        (dummy_input["input_ids"], dummy_input["attention_mask"]),
        onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "last_hidden_state": {0: "batch", 1: "sequence"}
        },
        opset_version=14
    )
    print("✅ Xuất ONNX thành công:", onnx_path)

# ======================
# 4. ONNX Inference
# ======================
print("\n🔹 ONNX Inference")
ort_session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

# Tokenize cho ONNX (numpy tensors)
tokens = tokenizer(sentences, padding=True, truncation=True, return_tensors="np")

# ⚡ Fix: ép kiểu sang int64
inputs_onnx = {
    "input_ids": tokens["input_ids"].astype(np.int64),
    "attention_mask": tokens["attention_mask"].astype(np.int64)
}

start = time.time()
outputs = ort_session.run(["last_hidden_state"], inputs_onnx)
end = time.time()

embeddings_onnx = outputs[0][:, 0, :]  # lấy vector [CLS]
print("Embeddings shape (ONNX):", embeddings_onnx.shape)
print("Time (ONNX): %.4f s" % (end - start))




```
---

## 4️⃣ Cách chạy

Trong thư mục chứa script:

```bash
python PyTorchvsONNXRuntime.py
```

---

## 5️⃣ Kết quả mẫu (thực tế Quadro M5000, CPU test)

```
🔹 PyTorch Inference
Embeddings shape (PyTorch): (3, 384)
Time (PyTorch): 1.5623 s

⚡ Dùng lại ONNX model đã có: model.onnx

🔹 ONNX Inference
Embeddings shape (ONNX): (3, 384)
Time (ONNX): 0.0320 s
```

👉 **ONNX nhanh hơn \~48 lần** 🚀

---

## 6️⃣ Nhận xét

* **PyTorch**:

  * Linh hoạt cho huấn luyện & nghiên cứu.
  * Tích hợp autograd, debug dễ.
  * Nhưng inference chậm do overhead.

* **ONNX Runtime**:

  * Chuyên dụng cho inference.
  * Tối ưu kernel cho CPU/GPU/ARM.
  * Nhẹ, nhanh, dễ deploy (C++, Java, .NET, Python).
  * Hỗ trợ quantization (FP16, INT8) → tối ưu thêm nữa.

---

## 7️⃣ Mở rộng

Anh có thể thử:

1. **Benchmark nhiều vòng lặp** (ví dụ chạy 100 lần, lấy trung bình).
2. **Batch lớn** (100 → 1000 câu) để xem scaling.
3. **ONNX quantization**:

```bash
pip install onnxruntime-tools
```

```python
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic("model.onnx", "model_quant.onnx", weight_type=QuantType.QInt8)
```

→ giảm dung lượng, tăng tốc thêm.

---

📌 Như vậy tài liệu này đã gồm: cài đặt, script đầy đủ, cách chạy, kết quả, phân tích, mở rộng.

---

Anh có muốn em viết thêm phần **benchmark nhiều vòng (ví dụ 100 lần chạy, đo trung bình và độ lệch chuẩn)** để đưa vào báo cáo so sánh cho đẹp hơn không?
