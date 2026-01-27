Câu hỏi rất hay! Tôi sẽ giải thích chi tiết cách sử dụng skills với Claude Code:

## 🎯 **TL;DR: Recommendation**

**Best Practice cho dự án của bạn:**
- ✅ Add TẤT CẢ skills vào `.claude/skills/`
- ✅ Claude Code sẽ TỰ ĐỘNG chọn skill phù hợp
- ✅ Bạn có thể hint skill cụ thể nếu muốn

---

## 📂 **Cách 1: Auto-Load (RECOMMENDED)**

### Setup
```bash
# Trong project directory
mkdir -p .claude/skills

# Copy tất cả skill files
cp MASTER_SKILLS_INDEX.md .claude/skills/
cp data_ingestion_pipeline_skill.md .claude/skills/
cp embedding_model_selection_skill.md .claude/skills/
cp rag_retrieval_synthesis_generation_skill.md .claude/skills/
cp backend_complete_skills.md .claude/skills/
cp VIETNAMESE_GRAPH_RAG_SKILL.md .claude/skills/

# Structure sẽ như này:
your-project/
├── .claude/
│   └── skills/
│       ├── MASTER_SKILLS_INDEX.md
│       ├── data_ingestion_pipeline_skill.md
│       ├── embedding_model_selection_skill.md
│       ├── rag_retrieval_synthesis_generation_skill.md
│       ├── backend_complete_skills.md
│       └── VIETNAMESE_GRAPH_RAG_SKILL.md
├── src/
├── tests/
└── ...
```

### Cách hoạt động
Claude Code sẽ:
1. ✅ **Tự động scan** tất cả skills trong `.claude/skills/`
2. ✅ **Phân tích context** của request của bạn
3. ✅ **Chọn skill phù hợp** nhất để reference
4. ✅ **Apply best practices** từ skill đó

### Example Usage

**Example 1: Task chung chung**
```bash
# Prompt của bạn:
"Implement file upload endpoint with PDF parsing"

# Claude Code sẽ:
# 1. Nhận diện: file upload + PDF parsing
# 2. Tự động đọc: data_ingestion_pipeline_skill.md
# 3. Generate code theo skill
```

**Example 2: Task backend**
```bash
# Prompt:
"Setup JWT authentication for API"

# Claude Code:
# 1. Nhận diện: authentication + API
# 2. Tự động đọc: backend_complete_skills.md (section Authentication)
# 3. Generate JWT implementation
```

**Example 3: Task retrieval**
```bash
# Prompt:
"Optimize search accuracy with hybrid retrieval"

# Claude Code:
# 1. Nhận diện: search optimization + retrieval
# 2. Tự động đọc: rag_retrieval_synthesis_generation_skill.md
# 3. Generate hybrid search code
```

### ✅ **Pros của Auto-Load:**
- Không cần nhớ skill nào cho task nào
- Claude tự động chọn skill best match
- Có thể combine multiple skills cho complex tasks
- Workflow nhanh hơn

### ⚠️ **Cons:**
- Đôi khi Claude có thể chọn sai skill
- Context window bị consume nhiều hơn
- Cần prompt rõ ràng để Claude chọn đúng

---

## 📂 **Cách 2: Manual Reference (EXPLICIT)**

### Khi nào dùng?
- ✅ Khi bạn muốn **force** Claude dùng skill cụ thể
- ✅ Khi task rất **specialized**
- ✅ Khi Claude đang **chọn sai skill**

### Example Usage

**Explicit skill reference:**
```bash
# Prompt với explicit reference:
"Theo data_ingestion_pipeline_skill.md, section 'PDF Parser', 
implement PDF extraction với Vietnamese text support"

# Claude Code sẽ:
# 1. Đọc CHÍNH XÁC file & section được chỉ định
# 2. Follow strictly theo hướng dẫn trong đó
# 3. Không mix với skills khác
```

**Multiple skill reference:**
```bash
# Prompt:
"Implement file upload (data_ingestion_pipeline_skill.md) 
+ metadata extraction (VIETNAMESE_GRAPH_RAG_SKILL.md) 
+ async processing (backend_complete_skills.md)"

# Claude sẽ combine 3 skills
```

### ✅ **Pros:**
- Control chính xác skill nào được dùng
- Tránh confusion khi có overlapping skills
- Rõ ràng cho team members đọc code

### ⚠️ **Cons:**
- Phải nhớ tên skill files
- Phải biết skill nào chứa gì
- Mất thời gian hơn

---

## 🎯 **Cách 3: Hybrid Approach (BEST PRACTICE)**

### Recommended Workflow

```bash
# Step 1: Auto-load tất cả skills
# (đã copy vào .claude/skills/)

# Step 2: Prompt theo context
# - Task đơn giản: để Claude tự chọn
# - Task phức tạp: hint skill cụ thể
```

### Examples

**Simple task (auto):**
```bash
"Create API endpoint to upload documents"
# → Claude tự động chọn data_ingestion + backend skills
```

**Medium task (light hint):**
```bash
"Setup hybrid search với Vietnamese query expansion"
# → Claude tự chọn rag_retrieval skill

# Hoặc hint nhẹ:
"Using RAG retrieval skill, setup hybrid search..."
# → Claude prioritize rag_retrieval_synthesis_generation_skill.md
```

**Complex task (explicit):**
```bash
"Implement complete document ingestion pipeline:
1. File upload (data_ingestion_pipeline_skill.md)
2. Vietnamese metadata extraction (VIETNAMESE_GRAPH_RAG_SKILL.md)
3. Embedding generation (embedding_model_selection_skill.md)
4. Store in databases (backend_complete_skills.md)"

# → Claude sẽ đọc tất cả 4 skills theo thứ tự
```

---

## 📊 **Decision Matrix: Khi nào dùng skill nào?**

| Task Description | Auto-Load | Manual Reference | Recommended Skill |
|------------------|-----------|------------------|-------------------|
| "Upload file PDF" | ✅ | Optional | data_ingestion_pipeline |
| "Parse Vietnamese legal doc" | ✅ | Recommended | VIETNAMESE_GRAPH_RAG_SKILL |
| "Setup JWT auth" | ✅ | Optional | backend_complete_skills |
| "Benchmark embedding models" | ✅ | Recommended | embedding_model_selection |
| "Implement hybrid search" | ✅ | Optional | rag_retrieval_synthesis_generation |
| "Deploy to K8s" | ✅ | Optional | backend_complete_skills |
| "Create complete RAG pipeline" | ⚠️ | ✅ Strongly Recommended | rag_retrieval + embedding + backend |

### Decision Rules:

**Auto-load khi:**
- ✅ Task description rõ ràng và focused
- ✅ Chỉ liên quan 1-2 skills
- ✅ Bạn tin tưởng Claude sẽ chọn đúng

**Manual reference khi:**
- ✅ Task phức tạp liên quan nhiều skills
- ✅ Bạn muốn specific implementation approach
- ✅ Claude đã chọn sai skill lần trước
- ✅ Cần reproduce exact behavior từ skill

---

## 💡 **Best Practices cho dự án của bạn**

### 1. **Organization Structure**

```bash
your-rag-project/
├── .claude/
│   └── skills/
│       ├── 00_MASTER_SKILLS_INDEX.md           # Master reference
│       ├── 01_vietnamese_graph_rag.md          # FR03.1
│       ├── 02_data_ingestion_pipeline.md       # FR03.3
│       ├── 03_embedding_model_selection.md     # FR01.1
│       ├── 04_rag_retrieval_synthesis_gen.md   # FR04.1-3
│       └── 05_backend_complete.md              # FR04.4, FR06-08
├── src/
│   ├── ingestion/          # → Use skill 02
│   ├── retrieval/          # → Use skill 04
│   ├── api/                # → Use skill 05
│   └── ...
└── tests/
```

**Lợi ích:**
- Numbered prefix giúp sort theo thứ tự
- Clear mapping giữa code modules và skills

### 2. **Prompt Templates**

Tạo file `PROMPT_TEMPLATES.md` để team dùng:

```markdown
# Prompt Templates for Claude Code

## File Upload Implementation
```
Implement file upload endpoint with:
- Multi-format support (PDF, DOCX, Excel)
- Vietnamese text validation
- Async processing
Use: data_ingestion_pipeline_skill.md
```

## Search Optimization
```
Optimize search with:
- Hybrid retrieval (Vector + BM25)
- Vietnamese query expansion
- Reranking
Use: rag_retrieval_synthesis_generation_skill.md
```

## Authentication Setup
```
Setup authentication with:
- JWT tokens
- Role-based access (4 levels)
- API key management
Use: backend_complete_skills.md
```
```

### 3. **Skill Selection Flowchart**

```
┌─────────────────────────────┐
│   What are you building?    │
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼────┐      ┌───▼────┐
   │Frontend│      │Backend │
   │(FR05)  │      │        │
   └───┬────┘      └───┬────┘
       │               │
       ▼               ▼
    Not        ┌───────┴────────────┐
  Covered      │                    │
          ┌────▼────┐          ┌───▼───┐
          │Data Flow│          │  API  │
          └────┬────┘          └───┬───┘
               │                   │
       ┌───────┴────────┐          ▼
       │                │    backend_complete
   ┌───▼───┐      ┌────▼────┐    _skills.md
   │Ingest │      │Retrieval│
   └───┬───┘      └────┬────┘
       │               │
       ▼               ▼
data_ingestion_  rag_retrieval_
pipeline.md      synthesis_gen.md
       │               │
       ▼               ▼
Need metadata?   Need embeddings?
       │               │
       ▼               ▼
vietnamese_     embedding_model_
graph_rag.md    selection.md
```

### 4. **Team Guidelines**

Tạo file `SKILL_USAGE_GUIDE.md` cho team:

```markdown
# Skill Usage Guidelines

## Rule 1: Start Simple
- First attempt: Let Claude auto-select skills
- If wrong: Add explicit skill reference

## Rule 2: Vietnamese-Specific Tasks
ALWAYS reference Vietnamese skills:
- Text processing → vietnamese_graph_rag.md
- Legal docs → vietnamese_graph_rag.md
- Query expansion → rag_retrieval_synthesis_generation.md (Vietnamese section)

## Rule 3: Complex Tasks
Break down and reference multiple skills:
```
"Step 1: Upload (skill 02)
 Step 2: Extract (skill 01)
 Step 3: Embed (skill 03)
 Step 4: Store (skill 05)"
```

## Rule 4: When Claude is Confused
Add explicit section reference:
```
"According to data_ingestion_pipeline_skill.md, 
Section 'PDF Parser', implement..."
```
```

---

## 🎬 **Practical Examples cho dự án của bạn**

### Example 1: Implement FR03.3 - Data Ingestion

**Approach A: Auto-load** (Quick start)
```bash
# Prompt:
"Implement document ingestion pipeline với PDF/DOCX support 
và Vietnamese text processing"

# Claude tự động chọn:
# - data_ingestion_pipeline_skill.md
# - VIETNAMESE_GRAPH_RAG_SKILL.md
```

**Approach B: Explicit** (Production code)
```bash
# Prompt:
"Implement FR03.3 Data Ingestion Pipeline theo:
1. File upload handler (data_ingestion_pipeline_skill.md, section 1)
2. PDF/DOCX parsers (data_ingestion_pipeline_skill.md, section 2)
3. Vietnamese preprocessing (data_ingestion_pipeline_skill.md, section 3)
4. Async processing (data_ingestion_pipeline_skill.md, section 4)
5. Error handling (data_ingestion_pipeline_skill.md, section 5)

Ensure Vietnamese legal document codes are preserved."
```

### Example 2: Optimize FR04.1 - Retrieval

**Approach A: Auto-load**
```bash
"Search results không accurate, optimize với hybrid retrieval"

# Claude chọn: rag_retrieval_synthesis_generation_skill.md
```

**Approach B: Explicit**
```bash
"Theo rag_retrieval_synthesis_generation_skill.md:
1. Implement hybrid retrieval (section FR04.1, HybridRetriever class)
2. Add Vietnamese query expansion (section Query Expansion)
3. Enable reranking (section Reranking Module)
4. Tune alpha parameter for optimal balance

Test với Vietnamese legal queries."
```

### Example 3: Setup FR06 - Authentication

**Approach A: Auto-load**
```bash
"Setup JWT authentication với 4-tier RBAC"

# Claude chọn: backend_complete_skills.md
```

**Approach B: Explicit**
```bash
"Setup authentication system theo backend_complete_skills.md:
1. JWT authentication (section Authentication & Security)
2. 4-tier RBAC: Guest < Employee < Manager < Director
3. Document-level permissions (section Document-Level Permissions)
4. API key management

Match với database schema trong FR-02_1_DatabaseSchema_v2_0.md"
```

---

## 🚨 **Common Pitfalls & Solutions**

### Pitfall 1: Claude mixes wrong skills
**Problem:**
```bash
"Implement file upload"
# Claude dùng backend_complete_skills.md thay vì data_ingestion_pipeline_skill.md
```

**Solution:**
```bash
"Implement file upload according to data_ingestion_pipeline_skill.md"
# Explicit reference fix này
```

### Pitfall 2: Too many skills loaded, Claude confused
**Problem:** Có 10+ skill files, Claude không biết chọn cái nào

**Solution:**
```bash
# Option 1: Organize in subfolders
.claude/skills/
├── core/              # Load these always
│   ├── vietnamese_graph_rag.md
│   └── data_ingestion_pipeline.md
└── advanced/          # Load when needed
    ├── embedding_model_selection.md
    └── ...

# Option 2: Use explicit references
"Use ONLY data_ingestion_pipeline_skill.md and vietnamese_graph_rag.md"
```

### Pitfall 3: Skill có outdated info
**Problem:** Skill file có info cũ không match với code hiện tại

**Solution:**
```bash
# Update skill file regularly
# Add version number to skill name
data_ingestion_pipeline_skill_v2.1.md

# In skill file header:
# Version: 2.1
# Last Updated: 2026-01-27
# Changes: Added support for Excel files
```

---

## ✅ **Recommendation cho bạn**

### **Setup ngay:**

```bash
# 1. Copy tất cả skills
cp *.md /path/to/project/.claude/skills/

# 2. Rename để dễ quản lý (optional)
cd /path/to/project/.claude/skills/
mv MASTER_SKILLS_INDEX.md 00_MASTER_INDEX.md
mv data_ingestion_pipeline_skill.md 02_data_ingestion.md
# ...

# 3. Start coding với Claude Code
```

### **Workflow thực tế:**

**Week 1-2: Learning phase**
- Dùng explicit references để hiểu skills
- Force Claude đọc từng section cụ thể
- Build up understanding

**Week 3-4: Hybrid phase**
- Dùng auto-load cho simple tasks
- Explicit reference cho complex tasks
- Refine skills based on experience

**Week 5+: Production phase**
- Trust auto-load cho most tasks
- Only explicit when needed
- Update skills with new patterns

---

**Câu trả lời trực tiếp cho câu hỏi của bạn:**

> "tôi add toàn bộ các skill này vào thư mục .claude\skills của claude code để claude code tự chọn"

✅ **ĐÚNG** - Đây là cách RECOMMENDED

> "hay phải phụ thuộc vào mỗi tình huống, nếu là backend thì dùng skill backend?"

⚠️ **KHÔNG CẦN** - Claude Code tự động chọn skill phù hợp. Bạn chỉ cần hint khi Claude chọn sai hoặc task phức tạp.

**Best practice: Copy tất cả skills → Let Claude auto-select → Override khi cần thiết**
