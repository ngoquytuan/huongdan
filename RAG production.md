
> 🎯 **Mục tiêu**: Giúp bạn xây dựng RAG hiệu quả, tránh over-engineering, biết cái nào nên làm trước – cái nào để sau.

---

# 🟩 **I. NHÓM MUST-HAVE (Cần có để RAG hoạt động tốt trong thực tế)**

Các kỹ thuật này **hầu như mọi hệ RAG production đều cần**, mang lại cải thiện rõ rệt về độ chính xác.

### **1. Chunking hiệu quả**

* **Sliding Window Chunking**
* **Semantic Chunking (nếu cần)**

→ Giảm mất ngữ cảnh, tăng chất lượng embedding.

---

### **2. Metadata Enrichment**

Tag: ngày, loại tài liệu, tác giả, domain…
→ Cho phép filter trước khi search → tăng độ chính xác gấp nhiều lần.

---

### **3. Hybrid Search**

Kết hợp:

* Keyword (BM25)
* Vector search (semantic)

→ Đây là tiêu chuẩn vàng của RAG.

---

### **4. Reranking / Cross-Encoder Rescoring**

Nhận top-k rồi re-score bằng model mạnh hơn.
→ *Đóng vai trò quan trọng nhất trong ranking hiện đại.*

---

### **5. Contextual Compression**

Loại bỏ phần không liên quan trong chunk trước khi gửi LLM.
→ Giảm token, tăng độ tập trung, giảm hallucination.

---

### **6. Citation Tracking / Source Linking**

Bắt buộc trong:

* enterprise
* legal
* medical
* financial

→ Giúp người dùng tin tưởng và dễ audit.

---

# 🟦 **II. NHÓM NÊN CÓ (Tối ưu hóa mạnh nhưng không bắt buộc)**

Dùng để **tăng chất lượng RAG lên tầm production-grade cao**.

### **1. Multi-Query Retrieval**

Tăng recall bằng cách sinh nhiều phiên bản query.
→ Hiệu quả khi tài liệu đa dạng / mơ hồ.

---

### **2. HyDE (Hypothetical Document Embeddings)**

LLM sinh câu trả lời giả → embed.
→ Tăng recall khi dữ liệu không khớp từ khóa của người dùng.

---

### **3. MMR (Maximal Marginal Relevance)**

Giảm trùng lặp, tăng đa dạng trong kết quả.
→ Rất hữu ích khi tài liệu nhiều phần tương tự.

---

### **4. Document Hierarchies (Parent / Child)**

Index child nhưng gửi parent vào LLM.
→ Cực kỳ tốt để giữ coherence.

---

### **5. Sentence Window Retrieval**

Retrieval ở mức câu và mở rộng sang hàng xóm.
→ Rất hiệu quả khi dữ liệu dạng luận văn, báo cáo, luật.

---

### **6. Context Window Packing**

Tối ưu số chunk trong context.
→ Giảm lãng phí token.

---

### **7. Negative Sampling (train retriever)**

Nếu bạn build retriever riêng thì dùng, còn không thì không cần.

---

# 🟨 **III. NHÓM ADVANCED / TÙY TRƯỜNG HỢP (chỉ dùng khi cần hoặc ở mức RAG 2.5 – 3.0)**

Nhóm này mang lại lợi ích nhưng chỉ khi hệ thống đạt quy mô lớn hoặc query phức tạp.

### **1. Adaptive Retrieval**

Tự chọn chiến lược retriever tùy query.
→ Giống “router” trong RAG 3.0.

---

### **2. Recursive Retrieval / Multi-hop Retrieval**

Khi cần:

* suy luận theo tầng
* dữ liệu phân cấp
* tìm từ tổng quan → chi tiết

---

### **3. Auto-Merging Retrieval**

Cho LLM đọc chunk lớn hơn khi nhiều child được retrieve.
→ Tăng coherence nhưng tăng token.

---

### **4. Graph-based Retrieval**

Dùng knowledge graph hoặc entity graph.
→ Hữu ích cho domain pháp lý, y khoa, enterprise, nhưng rất phức tạp.

---

### **5. Temporal Context Decay**

Ưu tiên tài liệu mới hơn.
→ Dùng trong:

* news
* financial
* logs

---

### **6. Context Ablation Testing**

Dùng để **đánh giá & tối ưu hệ thống**, không phải xử lý runtime.
→ Tìm chunk thực sự cần thiết.

---

# 🟥 **IV. NHÓM NỀN TẢNG / TƯ DUY KHÔNG PHẢI KỸ THUẬT CỤ THỂ**

Nhưng cực quan trọng trong RAG:

### **Lost in the Middle Problem**

Hiện tượng model bỏ qua đoạn giữa.
→ Quan trọng để thiết kế prompt & packing.

---

# 🎯 TÓM TẮT 3 NHÓM THEO MỨC ĐỘ QUAN TRỌNG

## 🟩 **MUST-HAVE — Bắt buộc**

| Kỹ thuật                  | Lợi ích chính                    |
| ------------------------- | -------------------------------- |
| Sliding Window Chunking   | Giảm mất ngữ cảnh                |
| Metadata Enrichment       | Lọc chính xác                    |
| Hybrid Search             | Vừa semantic vừa keyword         |
| Reranking / Cross-Encoder | Tăng precision mạnh              |
| Contextual Compression    | Tăng focus, giảm token           |
| Citation Tracking         | Tính minh bạch, enterprise-ready |

---

## 🟦 **NÊN CÓ — Tăng chất lượng mạnh**

* Multi-Query Retrieval
* HyDE
* MMR
* Document Hierarchies
* Sentence Window Retrieval
* Context Packing
* Negative Sampling (nếu training retriever)

---

## 🟨 **ADVANCED — Dùng tùy hệ thống**

* Adaptive Retrieval
* Recursive Retrieval
* Auto-Merging
* Graph-based Retrieval
* Temporal Decay
* Context Ablation Testing

---


### 🔧 **(1) Tạo kiến trúc RAG tối ưu dành cho bạn, dùng các kỹ thuật trên**

### 📊 **(2) So sánh mức cải thiện của từng kỹ thuật theo phần trăm (ước lượng industry)**

### 🔍 **(3) Gợi ý pipeline RAG chuẩn SaaS / enterprise**

