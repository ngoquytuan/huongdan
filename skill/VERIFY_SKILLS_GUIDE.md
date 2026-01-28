# How to Verify Skills are Loaded in Claude Code

## 🎯 Quick Verification Methods

### Method 1: Direct Ask (Simplest)

**Prompt Claude Code:**
```
Claude, bạn có thấy skill files nào trong project này không? 
Liệt kê tất cả các skill files bạn có thể truy cập.
```

**Expected Response nếu skills đã load:**
```
Tôi có thể thấy các skill files sau:
1. VIETNAMESE_GRAPH_RAG_SKILL.md
2. data_ingestion_pipeline_skill.md
3. embedding_model_selection_skill.md
4. rag_retrieval_synthesis_generation_skill.md
5. backend_complete_skills.md
6. debugging_troubleshooting_skill.md
7. MASTER_SKILLS_INDEX.md
```

**Dấu hiệu skills CHƯA load:**
- Claude trả lời: "Tôi không thấy skill files nào"
- Claude nói: "I don't have access to those files"
- Claude liệt kê sai hoặc thiếu files

---

### Method 2: Test Specific Knowledge (Recommended)

Test xem Claude có kiến thức cụ thể từ skills không:

#### Test 1: Vietnamese NLP Knowledge
**Prompt:**
```
Claude, theo VIETNAMESE_GRAPH_RAG_SKILL.md, 
cách tốt nhất để extract legal document codes từ Vietnamese text là gì?
```

**Expected Response nếu đã load:**
```python
Theo skill file, cần dùng regex patterns sau:

VIET_PATTERNS = {
    'legal_doc_number': r'Số\s*[:：]\s*(\d+/[\w-]+)',
    'decision_number': r'Quyết định số\s*(\d+/QĐ-[\w-]+)',
    'regulation_number': r'Nghị định số\s*(\d+/NĐ-CP)',
    ...
}

# [Claude sẽ quote exact code từ skill file]
```

**Dấu hiệu CHƯA load:**
- Claude đưa generic answer không specific
- Claude không cite skill file
- Claude nói "I don't have that information"

#### Test 2: Debugging Knowledge
**Prompt:**
```
Claude, theo debugging_troubleshooting_skill.md,
khi gặp UnicodeDecodeError với Vietnamese text, diagnostic script nào tôi nên chạy?
```

**Expected Response nếu đã load:**
```python
Theo debugging skill, bạn nên chạy:

def debug_file_encoding(filepath):
    import chardet
    
    with open(filepath, 'rb') as f:
        raw_data = f.read()
    
    detection = chardet.detect(raw_data)
    print(f"Detected encoding: {detection['encoding']}")
    ...

# [Claude sẽ provide exact function từ skill]
```

#### Test 3: Architecture Knowledge
**Prompt:**
```
Claude, trong data_ingestion_pipeline_skill.md,
file upload handler có những validation steps nào?
```

**Expected Response nếu đã load:**
```
Theo skill file, validation steps include:

1. Check file extension against allowed list
2. Verify file size (max 100MB)
3. Check file is not empty
4. Compute hash for deduplication
...

# [Claude sẽ list exact steps từ skill]
```

---

### Method 3: Test Code Generation Quality

**Prompt:**
```
Claude, hãy implement file upload endpoint với validation 
theo data_ingestion_pipeline_skill.md
```

**Dấu hiệu skills ĐÃ load:**
```python
# Claude sẽ generate code giống trong skill file:

from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import hashlib

class UploadManager:
    async def upload_file(self, file: UploadFile, ...):
        # 1. Validate file
        validation_result = await self.validate_file(file)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, ...)
        
        # 2. Generate unique filename
        file_hash = await self.compute_hash(file)
        ...
        
# [Code sẽ follow structure trong skill file]
```

**Dấu hiệu skills CHƯA load:**
- Code generic, không theo pattern trong skill
- Thiếu validation steps
- Không có error handling như skill
- Structure khác hoàn toàn

---

### Method 4: Reference Test

**Prompt:**
```
Claude, trong MASTER_SKILLS_INDEX.md có bao nhiêu skill files?
Và Quick Task Finder table có bao nhiêu entries?
```

**Expected Response nếu đã load:**
```
Trong MASTER_SKILLS_INDEX.md có:
- 6 main skill files (+ 1 user-provided)
- Quick Task Finder table có khoảng 40+ entries
- Covers các module: FR01, FR03, FR04, FR06-08, Testing, Deployment, Debugging
```

---

## 🔍 Comprehensive Verification Script

Tạo file test này và chạy với Claude Code:

```python
# verify_skills_loaded.py

"""
Verification script to test if Claude Code has loaded all skills
Run this with Claude Code and ask Claude to execute it
"""

def test_skill_access():
    """
    Test if Claude can access skill files
    """
    print("="*60)
    print("SKILL VERIFICATION TEST")
    print("="*60)
    
    skill_files = [
        "VIETNAMESE_GRAPH_RAG_SKILL.md",
        "data_ingestion_pipeline_skill.md",
        "embedding_model_selection_skill.md",
        "rag_retrieval_synthesis_generation_skill.md",
        "backend_complete_skills.md",
        "debugging_troubleshooting_skill.md",
        "MASTER_SKILLS_INDEX.md"
    ]
    
    print("\nTest 1: List all skill files")
    print("-" * 60)
    print("Expected skill files:")
    for i, skill in enumerate(skill_files, 1):
        print(f"{i}. {skill}")
    
    print("\n" + "="*60)
    print("VERIFICATION QUESTIONS FOR CLAUDE")
    print("="*60)
    
    questions = [
        {
            "question": "What are the 5 document types in VIETNAMESE_GRAPH_RAG_SKILL.md?",
            "expected": "LEGAL_RND, HR_POLICY, IT_MANUAL, GEN_REPORT, GENERAL",
            "skill": "VIETNAMESE_GRAPH_RAG_SKILL.md"
        },
        {
            "question": "What is the default embedding model in embedding_model_selection_skill.md?",
            "expected": "Qwen/Qwen3-Embedding-0.6B with 1024 dimensions",
            "skill": "embedding_model_selection_skill.md"
        },
        {
            "question": "In data_ingestion_pipeline_skill.md, what's the max file upload size?",
            "expected": "100MB (100 * 1024 * 1024 bytes)",
            "skill": "data_ingestion_pipeline_skill.md"
        },
        {
            "question": "In rag_retrieval_synthesis_generation_skill.md, what are the 3 main components?",
            "expected": "Retrieval (FR04.1), Synthesis (FR04.2), Generation (FR04.3)",
            "skill": "rag_retrieval_synthesis_generation_skill.md"
        },
        {
            "question": "In backend_complete_skills.md, what are the 4 role levels?",
            "expected": "Guest, Employee, Manager, Director",
            "skill": "backend_complete_skills.md"
        },
        {
            "question": "In debugging_troubleshooting_skill.md, what tool debugs UnicodeDecodeError?",
            "expected": "debug_file_encoding() function",
            "skill": "debugging_troubleshooting_skill.md"
        }
    ]
    
    print("\nPlease answer these questions to verify skill access:\n")
    
    for i, q in enumerate(questions, 1):
        print(f"Question {i}:")
        print(f"  From: {q['skill']}")
        print(f"  Q: {q['question']}")
        print(f"  Expected: {q['expected']}")
        print()
    
    print("="*60)
    print("INSTRUCTIONS FOR CLAUDE")
    print("="*60)
    print("""
If you can answer ALL questions correctly with details from the skill files:
    ✅ Skills are loaded successfully
    
If you can only answer some or give generic answers:
    ⚠️ Skills may be partially loaded
    
If you cannot answer or say you don't have access:
    ❌ Skills are NOT loaded
    """)

if __name__ == "__main__":
    test_skill_access()
```

**How to use:**
1. Save file as `verify_skills_loaded.py` in project
2. Prompt Claude Code:
   ```
   Claude, hãy chạy file verify_skills_loaded.py 
   và trả lời tất cả các questions trong output
   ```

---

## 🚨 Signs Skills Are NOT Loaded

### Red Flags:
1. ❌ Claude says "I don't have access to those files"
2. ❌ Claude gives generic answers instead of specific code
3. ❌ Claude cannot cite skill file sections
4. ❌ Claude doesn't mention skill files when asked
5. ❌ Generated code doesn't follow patterns in skills
6. ❌ Claude cannot list skill files
7. ❌ Claude gives wrong information contradicting skills

### Example of NOT loaded:
**You ask:**
```
Claude, theo data_ingestion_pipeline_skill.md, 
làm sao validate file upload?
```

**Claude responds:**
```
Để validate file upload, bạn nên:
- Kiểm tra file size
- Kiểm tra extension
- Scan virus
...

[Generic answer, không cite skill file, không có code examples]
```

**This means:** ❌ Skills NOT loaded

---

## ✅ Signs Skills ARE Loaded

### Green Flags:
1. ✅ Claude cites skill files by name
2. ✅ Claude provides exact code from skills
3. ✅ Claude mentions specific sections/functions
4. ✅ Generated code matches skill patterns
5. ✅ Claude can list all skill files
6. ✅ Claude references "according to [skill_name]"
7. ✅ Answers are highly specific, not generic

### Example of loaded:
**You ask:**
```
Claude, theo data_ingestion_pipeline_skill.md, 
làm sao validate file upload?
```

**Claude responds:**
```python
Theo data_ingestion_pipeline_skill.md, 
validation flow như sau:

async def validate_file(self, file: UploadFile) -> dict:
    # Allowed formats
    ALLOWED_EXTENSIONS = {
        '.pdf', '.docx', '.doc', '.txt', 
        '.html', '.xlsx', '.xls', '.csv'
    }
    
    # Max file size (100MB)
    MAX_SIZE = 100 * 1024 * 1024
    
    # Check extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"Unsupported file format: {file_ext}"
        }
    ...

[Exact code từ skill file, với comments và structure giống hệt]
```

**This means:** ✅ Skills loaded successfully!

---

## 🛠️ Troubleshooting: Skills Not Loading

### Issue 1: Skills not in project folder

**Solution:**
```bash
# Make sure skills are in project root or dedicated folder
project/
├── skills/
│   ├── VIETNAMESE_GRAPH_RAG_SKILL.md
│   ├── data_ingestion_pipeline_skill.md
│   ├── embedding_model_selection_skill.md
│   ├── rag_retrieval_synthesis_generation_skill.md
│   ├── backend_complete_skills.md
│   ├── debugging_troubleshooting_skill.md
│   └── MASTER_SKILLS_INDEX.md
├── src/
└── tests/
```

### Issue 2: Wrong file format

**Skills must be:**
- Markdown files (.md)
- UTF-8 encoded
- Properly formatted
- Not corrupted

**Test:**
```bash
# Check if files are readable
cat skills/MASTER_SKILLS_INDEX.md | head -20

# Check encoding
file -i skills/*.md

# Should show: text/plain; charset=utf-8
```

### Issue 3: Claude Code not in project mode

**Solution:**
Make sure you're using Claude Code in a project, not just chat.

**Verify:**
- You should see project name in Claude Code interface
- Files should be visible in sidebar
- Skills should be in project directory

### Issue 4: Skill files too large

**Check file sizes:**
```bash
ls -lh skills/*.md

# All files should be < 5MB
# If larger, might not load properly
```

### Issue 5: Skills not explicitly referenced

**Always reference skills in prompts:**

❌ Bad:
```
Claude, tạo file upload endpoint
```

✅ Good:
```
Claude, tạo file upload endpoint theo 
data_ingestion_pipeline_skill.md, 
section "File Upload Handler"
```

---

## 📋 Complete Verification Checklist

Use this checklist to verify skills are working:

```markdown
### Pre-verification Setup
☐ All skill files in project folder
☐ Files are .md format
☐ UTF-8 encoding
☐ Claude Code in project mode
☐ Can see files in sidebar

### Verification Tests
☐ Claude can list all skill files
☐ Claude can answer questions from each skill
☐ Claude generates code following skill patterns
☐ Claude cites skills by name
☐ Generated code has same structure as skills
☐ Claude provides specific, not generic answers

### Individual Skill Tests
☐ VIETNAMESE_GRAPH_RAG_SKILL.md - Can list 5 doc types
☐ data_ingestion_pipeline_skill.md - Can describe validation
☐ embedding_model_selection_skill.md - Can name default model
☐ rag_retrieval_synthesis_generation_skill.md - Can explain pipeline
☐ backend_complete_skills.md - Can list role levels
☐ debugging_troubleshooting_skill.md - Can provide debug scripts
☐ MASTER_SKILLS_INDEX.md - Can navigate to sections

### Final Confirmation
☐ Run verify_skills_loaded.py script
☐ All questions answered correctly
☐ Code generation quality is high
☐ Skills cited in responses

If ALL boxes checked: ✅ Skills loaded successfully!
If ANY box unchecked: ⚠️ Need troubleshooting
```

---

## 💡 Best Practices for Using Skills

### 1. Always Reference Skills Explicitly

❌ Don't:
```
Claude, tạo database schema
```

✅ Do:
```
Claude, tạo database schema theo FR-02_1_DatabaseSchema_v2_0.md
hoặc theo backend_complete_skills.md nếu file kia không có
```

### 2. Test After Major Changes

After adding/updating skills:
```
Claude, hãy verify lại xem bạn có thấy 
debugging_troubleshooting_skill.md mới không?
Nội dung chính là gì?
```

### 3. Use Master Index for Navigation

```
Claude, trong MASTER_SKILLS_INDEX.md,
tôi cần implement file upload. Skill nào tôi nên dùng?
```

### 4. Validate Generated Code

```
Claude, code bạn vừa generate có follow pattern 
trong data_ingestion_pipeline_skill.md không?
Hãy so sánh với skill file.
```

### 5. Request Specific Sections

```
Claude, hãy đọc section "Error Handling & Retry Logic" 
trong data_ingestion_pipeline_skill.md 
và implement theo đó
```

---

## 🎯 Quick Verification Command

**Copy-paste this into Claude Code:**

```
Claude, hãy verify skills đã load bằng cách:

1. List tất cả skill files bạn thấy trong project
2. Trả lời 3 questions này:
   a) Default embedding model là gì? (từ embedding_model_selection_skill.md)
   b) 4 role levels là gì? (từ backend_complete_skills.md)  
   c) Function nào debug UnicodeDecodeError? (từ debugging_troubleshooting_skill.md)
3. Generate 1 đoạn code ngắn theo bất kỳ skill nào và cite skill file

Nếu bạn trả lời được cả 3 với details từ skill files,
tức là skills đã load thành công! ✅
```

---

## 📊 Success Criteria

Skills are confirmed loaded when:

- ✅ Claude lists all 7 skill files correctly
- ✅ Claude answers specific questions from each skill
- ✅ Generated code matches skill patterns
- ✅ Claude cites skills by name
- ✅ Responses include exact code/text from skills
- ✅ No generic answers
- ✅ verify_skills_loaded.py test passes 100%

**If all criteria met: You're ready to start developing! 🚀**

---

## 🆘 Still Having Issues?

If skills still not loading after troubleshooting:

1. **Restart Claude Code session**
   - Close and reopen project
   - Skills may need refresh

2. **Check file permissions**
   ```bash
   chmod 644 skills/*.md
   ```

3. **Verify file integrity**
   ```bash
   # Files should not be corrupted
   head -5 skills/MASTER_SKILLS_INDEX.md
   tail -5 skills/MASTER_SKILLS_INDEX.md
   ```

4. **Try explicit loading**
   ```
   Claude, please read the file at skills/MASTER_SKILLS_INDEX.md
   and tell me what you see
   ```

5. **Contact support**
   - If none of above works
   - Provide verification test results
   - Share skill file structure

---

## End of Verification Guide
