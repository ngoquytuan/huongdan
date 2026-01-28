# 🎯 Quick Skill Verification Reference Card

## One-Liner Test (30 seconds)

**Copy-paste vào Claude Code:**
```
Claude, list tất cả skill files trong project và trả lời: 
Default embedding model là gì? (từ embedding_model_selection_skill.md)
```

**✅ Nếu Claude trả lời:** "Qwen/Qwen3-Embedding-0.6B with 1024 dimensions"
→ **Skills loaded!**

**❌ Nếu Claude nói:** "I don't have access" hoặc câu trả lời generic
→ **Skills NOT loaded!**

---

## Quick Test Methods (Choose one)

### Method A: List Test (1 minute)
```
Claude, bạn có thấy những skill files nào trong project này?
```

**Expected:** Claude lists 7 files:
1. VIETNAMESE_GRAPH_RAG_SKILL.md
2. data_ingestion_pipeline_skill.md
3. embedding_model_selection_skill.md
4. rag_retrieval_synthesis_generation_skill.md
5. backend_complete_skills.md
6. debugging_troubleshooting_skill.md
7. MASTER_SKILLS_INDEX.md

---

### Method B: Knowledge Test (2 minutes)
```
Claude, trả lời 3 questions:
1. Default embedding model? (embedding_model_selection_skill.md)
2. Max file upload size? (data_ingestion_pipeline_skill.md)
3. 4 role levels? (backend_complete_skills.md)
```

**Expected:**
1. Qwen/Qwen3-Embedding-0.6B (1024 dims)
2. 100MB
3. Guest → Employee → Manager → Director

---

### Method C: Code Gen Test (3 minutes)
```
Claude, generate file upload validation code 
theo data_ingestion_pipeline_skill.md
```

**Expected:** Code matches pattern in skill:
```python
async def validate_file(self, file: UploadFile) -> dict:
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', ...}
    MAX_SIZE = 100 * 1024 * 1024
    # ... (như trong skill file)
```

---

### Method D: Comprehensive Test (5 minutes)
```
Claude, chạy file test_skills_loaded.py 
và trả lời tất cả 15 questions
```

**Expected:** Score >= 85% (145/170 points)

---

## Quick Troubleshooting

### Skills not loading?

**Check 1:** Files in correct location?
```bash
ls skills/*.md
# Should list all 7 files
```

**Check 2:** Files readable?
```bash
head -5 skills/MASTER_SKILLS_INDEX.md
# Should show content
```

**Check 3:** Claude Code in project mode?
- Look for project name in interface
- Should see files in sidebar

**Check 4:** Restart Claude Code
- Close and reopen project
- Try verification again

---

## Success Indicators

### ✅ Skills ARE loaded:
- Claude lists all skill files correctly
- Claude cites skills by name
- Claude provides exact code from skills
- Generated code follows skill patterns
- Answers are specific, not generic
- Score >= 85% on test

### ❌ Skills NOT loaded:
- Claude says "don't have access"
- Cannot list skill files
- Gives generic answers
- Generated code doesn't match patterns
- No skill citations
- Score < 70% on test

---

## Emergency Verification Command

**If unsure, run this:**
```
Claude, verify skills với 3 steps:

1. List all .md files trong skills/ folder
2. Đọc MASTER_SKILLS_INDEX.md và summarize nội dung
3. Generate 1 function từ bất kỳ skill nào và cite source

Nếu làm được cả 3 → Skills loaded ✅
Nếu không → Skills NOT loaded ❌
```

---

## Best Practice

**Always reference skills explicitly:**

❌ Don't:
```
Claude, tạo API endpoint
```

✅ Do:
```
Claude, tạo API endpoint theo backend_complete_skills.md,
section "FastAPI Architecture"
```

---

## Quick Links

- **Full Guide:** VERIFY_SKILLS_GUIDE.md
- **Test Script:** test_skills_loaded.py
- **Master Index:** MASTER_SKILLS_INDEX.md
- **Troubleshooting:** debugging_troubleshooting_skill.md

---

## Score Interpretation

| Score | Grade | Status | Action |
|-------|-------|--------|--------|
| 160-170 | A+ | Excellent | ✅ Ready to develop |
| 145-159 | A | Good | ✅ Ready, minor checks |
| 120-144 | B | Fair | ⚠️ Review setup |
| < 120 | F | Fail | ❌ Troubleshoot |

---

**Printed:** `date +%Y-%m-%d`

**Version:** 1.0

**Quick Test:** 30 seconds
**Full Test:** 5 minutes
**Troubleshooting:** VERIFY_SKILLS_GUIDE.md
