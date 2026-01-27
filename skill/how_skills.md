Tôi sẽ tạo cho bạn một skill file chuyên biệt cho dự án Graph RAG của bạn! Đây là skill được thiết kế riêng cho Claude Code để hiểu rõ context và giúp bạn lập trình chính xác.Tôi đã tạo xong **skill file chuyên biệt** cho dự án Graph RAG của bạn! 

## 📋 Skill file bao gồm:

### **1. Project Context đầy đủ**
- Kiến trúc hệ thống (PostgreSQL + ChromaDB + BM25)
- 7-tier hierarchical classification cho văn bản Việt Nam
- 5 loại văn bản (LEGAL_RND, HR_POLICY, IT_MANUAL, GEN_REPORT, GENERAL)
- Metadata structure với 50+ fields

### **2. Vietnamese NLP Guidelines**
- Patterns và regex cho văn bản pháp lý Việt Nam
- Fuzzy matching cho tiếng Việt
- underthesea library best practices
- Vietnamese encoding handling

### **3. Development Best Practices**
- MetadataEnricher class patterns
- 3-layer extraction approach (regex + keywords + fuzzy)
- Hybrid workflow (auto + manual confirmation)
- Confidence scoring system

### **4. Testing Strategy**
- Unit tests cho 5 document types
- Integration tests cho full pipeline
- Relationship extraction testing (target 70%+ accuracy)
- Performance benchmarks

### **5. Upgrade Priorities**
- **HIGH**: Relationship extraction enhancement (40% → 70%+)
- **HIGH**: Metadata editor UI (Streamlit)
- **MEDIUM**: Manual chunking interface
- **MEDIUM**: Performance optimization

### **6. Code Examples**
- Vietnamese pattern matching
- Database integration (PostgreSQL + ChromaDB)
- Streamlit UI components
- Graph traversal optimization

## 🚀 Cách sử dụng với Claude Code:

### **Bước 1: Lưu skill file**
File đã được tạo và sẵn sàng download. Lưu nó vào thư mục skills của bạn.

### **Bước 2: Load vào Claude Code**
```bash
# Option 1: Đặt trong thư mục dự án
mkdir -p .claude/skills
cp VIETNAMESE_GRAPH_RAG_SKILL.md .claude/skills/

# Option 2: Load khi chạy Claude Code
claude-code --skill VIETNAMESE_GRAPH_RAG_SKILL.md
```

### **Bước 3: Sử dụng trong conversation**
Khi làm việc với Claude Code, skill này sẽ giúp LLM:
- ✅ Hiểu rõ context của dự án FR-03.1
- ✅ Code đúng patterns cho Vietnamese NLP
- ✅ Follow best practices cho RAG system
- ✅ Test và validate code chính xác
- ✅ Debug các issues về relationship extraction
- ✅ Optimize performance cho graph traversal

## 🎯 Example Usage:

```
Bạn: "Help me improve relationship extraction accuracy from 40% to 70%"

Claude Code (với skill): 
- Hiểu ngay đây là bottleneck chính
- Biết current approach (pattern matching)
- Suggest ML-based approach với embeddings similarity
- Provide code cho RelationshipSuggester class
- Include Vietnamese-specific patterns
- Add comprehensive tests
```

Skill file này hoàn toàn tailored cho dự án của bạn và sẽ giúp Claude Code lập trình chính xác hơn nhiều! 🎉
**Không hoàn toàn ổn** - có sự nhầm lẫn về cấu trúc và mục đích. Để tôi giải thích:

## 🔍 Sự khác biệt quan trọng:

### **1. Agents (.md với frontmatter)**
```yaml
---
name: python-ai-expert
description: Use this agent when...
model: sonnet
---
You are a Python AI/ML expert...
```
- **Mục đích**: Định nghĩa **persona/role** cho AI assistant
- **Cách hoạt động**: Thay đổi "personality" và expertise focus
- **Location**: `.claude/agents/`

### **2. Skills (knowledge/documentation)**
```markdown
# Vietnamese Graph RAG System Development Skill

## Overview
This skill enables Claude to assist with...
```
- **Mục đích**: Cung cấp **knowledge base** cho specific domain/project
- **Cách hoạt động**: Reference material Claude reads before coding
- **Location**: `.claude/skills/` hoặc `/mnt/skills/user/`

## ✅ Cấu trúc đúng nên là:

```
your-project/
├── .claude/
│   ├── agents/
│   │   └── python-ai-expert.md          # Agent definition
│   └── skills/
│       └── vietnamese-graph-rag.md      # Skill/knowledge base
```

## 🎯 Cách sử dụng hiệu quả:

### **Option 1: Tách riêng (RECOMMENDED)**
```bash
# Tạo cấu trúc thư mục
mkdir -p .claude/agents
mkdir -p .claude/skills

# Di chuyển files đúng vị trí
mv python-ai-expert.md .claude/agents/
mv VIETNAMESE_GRAPH_RAG_SKILL.md .claude/skills/vietnamese-graph-rag.md
```

**Khi sử dụng:**
```bash
# Load agent + skill
claude-code --agent python-ai-expert --skill vietnamese-graph-rag

# Or in conversation:
"@python-ai-expert với knowledge từ vietnamese-graph-rag skill, 
help me improve relationship extraction"
```

### **Option 2: Merge thành một agent tích hợp (ALTERNATIVE)**

Nếu bạn muốn có một agent chuyên biệt cho dự án này, có thể merge:

```yaml
---
name: vietnamese-rag-expert
description: Expert in Vietnamese Graph RAG system development
model: sonnet
---

You are a specialized Python AI/ML expert focused on Vietnamese Graph RAG systems.

[Include both: AI/ML expertise + Vietnamese RAG knowledge]
```

Nhưng option này **không linh hoạt** - không thể reuse python-ai-expert cho projects khác.

## 🚀 Recommendation cho dự án của bạn:

### **Best Practice Setup:**

```bash
.claude/
├── agents/
│   ├── python-ai-expert.md           # General AI/ML expertise
│   └── vietnamese-nlp-expert.md      # Vietnamese NLP specialist (optional)
│
└── skills/
    ├── vietnamese-graph-rag.md       # Your project knowledge
    ├── chromadb-integration.md       # ChromaDB best practices
    └── streamlit-ui-patterns.md      # UI development patterns
```

### **Usage Examples:**

```bash
# For coding tasks needing AI expertise + project knowledge
claude-code --agent python-ai-expert --skill vietnamese-graph-rag

# For Vietnamese NLP specific tasks
claude-code --agent vietnamese-nlp-expert --skill vietnamese-graph-rag

# For UI development
claude-code --agent python-ai-expert --skill streamlit-ui-patterns
```

## 🔧 Quick Fix cho bạn:

```bash
# 1. Tạo đúng cấu trúc
mkdir -p .claude/skills

# 2. Di chuyển skill file
mv .claude/agents/VIETNAMESE_GRAPH_RAG_SKILL.md .claude/skills/vietnamese-graph-rag.md

# 3. Giữ agent ở đúng chỗ
# .claude/agents/python-ai-expert.md (không đổi)

# 4. Test
claude-code --agent python-ai-expert --skill vietnamese-graph-rag
```

## 💡 Lợi ích của việc tách riêng:

1. **Reusability**: `python-ai-expert` dùng được cho nhiều projects
2. **Modularity**: Mix & match agents với skills khác nhau
3. **Maintainability**: Update skill knowledge không ảnh hưởng agent behavior
4. **Clarity**: Rõ ràng đâu là "who" (agent) và đâu là "what" (skill)

**Tóm lại**: Đặt cả hai vào `.claude/agents/` có thể work nhưng **không best practice**. Nên tách riêng để có kiến trúc rõ ràng và linh hoạt hơn! 🎯

**CÓ - Hoàn toàn được!** Và đây là điểm mạnh của Claude Code architecture. 🎯

## ✅ Multi-Agent & Multi-Skill Architecture

```
your-project/
├── .claude/
│   ├── agents/                    # Multiple agents ✓
│   │   ├── python-ai-expert.md
│   │   ├── vietnamese-nlp-expert.md
│   │   ├── database-architect.md
│   │   ├── ui-ux-developer.md
│   │   └── devops-engineer.md
│   │
│   └── skills/                    # Multiple skills ✓
│       ├── vietnamese-graph-rag.md
│       ├── chromadb-best-practices.md
│       ├── postgresql-optimization.md
│       ├── streamlit-ui-patterns.md
│       └── legal-document-classification.md
```

## 🎭 Khi nào dùng Multiple Agents?

### **Use Case 1: Different Expertise Areas**

```bash
# Backend development
claude-code --agent database-architect --skill postgresql-optimization
"Help me optimize graph traversal queries"

# Frontend development  
claude-code --agent ui-ux-developer --skill streamlit-ui-patterns
"Create metadata editor interface"

# AI/ML work
claude-code --agent python-ai-expert --skill vietnamese-graph-rag
"Improve relationship extraction to 70% accuracy"

# Deployment
claude-code --agent devops-engineer
"Set up Docker container for the RAG system"
```

### **Use Case 2: Task-Specific Specialists**

```bash
# Vietnamese NLP tasks
@vietnamese-nlp-expert "Extract legal document patterns from this text"

# General Python optimization
@python-ai-expert "Optimize batch processing for 100+ documents"

# Database design
@database-architect "Design schema for document relationships"
```

## 📚 Khi nào dùng Multiple Skills?

### **Use Case 1: Modular Knowledge Base**

```bash
# Load multiple skills for complex task
claude-code \
  --agent python-ai-expert \
  --skill vietnamese-graph-rag \
  --skill chromadb-best-practices \
  --skill legal-document-classification

"Implement end-to-end pipeline with ChromaDB integration"
```

### **Use Case 2: Different Contexts**

```bash
# Development phase
--skill vietnamese-graph-rag
--skill testing-strategies

# Deployment phase  
--skill docker-deployment
--skill performance-optimization

# Maintenance phase
--skill monitoring-alerting
--skill troubleshooting-guide
```

## 🎯 Recommended Setup cho dự án Vietnamese RAG của bạn:

### **Option A: Specialized Agents (RECOMMENDED)**

```
.claude/
├── agents/
│   ├── rag-architect.md           # System design & architecture
│   ├── vietnamese-nlp-expert.md   # Vietnamese text processing
│   ├── graph-db-expert.md         # Graph relationships & queries
│   └── ui-developer.md            # Streamlit interfaces
│
└── skills/
    ├── project-overview.md        # High-level project context
    ├── vietnamese-patterns.md     # Legal document patterns
    ├── metadata-schema.md         # Database schema details
    ├── extraction-algorithms.md   # Extraction logic & algorithms
    ├── relationship-detection.md  # Relationship extraction methods
    └── ui-components.md           # Streamlit component library
```

**Usage:**
```bash
# Working on metadata extraction
claude-code \
  --agent vietnamese-nlp-expert \
  --skill vietnamese-patterns \
  --skill extraction-algorithms

# Working on relationship detection
claude-code \
  --agent rag-architect \
  --skill relationship-detection \
  --skill graph-db-expert

# Working on UI
claude-code \
  --agent ui-developer \
  --skill ui-components \
  --skill metadata-schema
```

### **Option B: General + Specific Skills (SIMPLER)**

```
.claude/
├── agents/
│   ├── python-ai-expert.md        # One general expert
│   └── vietnamese-specialist.md   # One domain specialist
│
└── skills/
    ├── vietnamese-rag-core.md     # Core system knowledge
    ├── vietnamese-rag-ui.md       # UI-specific knowledge
    ├── vietnamese-rag-db.md       # Database-specific knowledge
    └── vietnamese-rag-deployment.md  # Deployment knowledge
```

**Usage:**
```bash
# Load relevant skill based on task
claude-code --agent python-ai-expert --skill vietnamese-rag-core
claude-code --agent python-ai-expert --skill vietnamese-rag-ui
claude-code --agent vietnamese-specialist --skill vietnamese-rag-core
```

## 💡 Best Practices:

### **1. Agent Granularity**

❌ **Too Many (Overkill):**
```
agents/
├── python-expert.md
├── pytorch-expert.md
├── tensorflow-expert.md
├── scikit-learn-expert.md
└── pandas-expert.md
```

✅ **Right Balance:**
```
agents/
├── python-ai-expert.md           # Covers all ML frameworks
├── vietnamese-nlp-expert.md      # Domain specialist
└── full-stack-developer.md       # UI + Backend
```

### **2. Skill Granularity**

❌ **Too Granular:**
```
skills/
├── regex-patterns.md
├── fuzzy-matching.md
├── confidence-scoring.md
└── error-handling.md
```

✅ **Well-Organized:**
```
skills/
├── vietnamese-rag-system.md      # Complete system overview
├── extraction-techniques.md      # All extraction methods
├── database-integration.md       # All DB-related info
└── ui-development.md             # All UI patterns
```

### **3. Combining Strategy**

```bash
# Simple tasks: 1 agent + 1 skill
claude-code --agent python-ai-expert --skill vietnamese-rag-core

# Complex tasks: 1 agent + multiple skills
claude-code --agent python-ai-expert \
  --skill vietnamese-rag-core \
  --skill database-integration \
  --skill testing-strategies

# Cross-domain tasks: Switch agents + combine skills
# First: Design with architect
claude-code --agent rag-architect --skill vietnamese-rag-core
# Then: Implement with AI expert
claude-code --agent python-ai-expert --skill extraction-techniques
# Finally: Build UI
claude-code --agent ui-developer --skill ui-development
```

## 🚀 Practical Example cho Project của bạn:

### **Scenario: Improve Relationship Extraction (40% → 70%)**

```bash
# Phase 1: Research & Design
claude-code \
  --agent rag-architect \
  --skill vietnamese-rag-core \
  --skill relationship-detection

Prompt: "Analyze current relationship extraction approach and 
design ML-based improvement strategy"

# Phase 2: Implementation
claude-code \
  --agent python-ai-expert \
  --skill vietnamese-rag-core \
  --skill extraction-techniques

Prompt: "Implement RelationshipSuggester class with embedding 
similarity and temporal logic"

# Phase 3: Database Optimization
claude-code \
  --agent graph-db-expert \
  --skill database-integration

Prompt: "Optimize PostgreSQL queries for parent-child relationship 
traversal with GIN indices"

# Phase 4: UI Integration
claude-code \
  --agent ui-developer \
  --skill ui-components \
  --skill metadata-schema

Prompt: "Create Streamlit interface for manual relationship 
confirmation with ML suggestions"

# Phase 5: Testing
claude-code \
  --agent python-ai-expert \
  --skill testing-strategies \
  --skill vietnamese-rag-core

Prompt: "Write comprehensive tests for relationship extraction 
to validate 70% accuracy target"
```

## 📊 Trade-offs:

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **1 Agent + 1 Big Skill** | Simple, all context in one place | Can be overwhelming, less modular | Small projects |
| **1 Agent + Multiple Skills** | Flexible, load only needed context | Need to know which skill to use | Medium projects |
| **Multiple Agents + Multiple Skills** | Maximum flexibility, clear separation | More complex to manage | Large projects |

## 🎯 My Recommendation for Your Project:

```
.claude/
├── agents/
│   ├── python-ai-expert.md          # Keep the one you have
│   └── vietnamese-rag-expert.md     # Create domain specialist
│
└── skills/
    ├── vietnamese-rag-system.md     # Rename từ file hiện tại
    ├── extraction-methods.md        # Chi tiết về extraction
    ├── ui-development.md            # Streamlit patterns
    └── testing-validation.md        # Testing strategies
```

**Why?** 
- 2 agents: enough specialization without complexity
- 4 skills: modular but not fragmented
- Easy to grow: add more as needed

**Tóm lại:** Đặt nhiều agents/skills không chỉ được phép mà còn là **best practice** cho projects phức tạp! Key là balance giữa modularity và simplicity. 🎯
**KHÔNG** - Không nên tạo agent riêng cho mỗi module! Đây là **anti-pattern** phổ biến. Để tôi giải thích chi tiết:

## 🎯 Nguyên tắc then chốt:

### **Agents = Expertise Domain (WHO)**
### **Skills = Knowledge Modules (WHAT)**

## ❌ Anti-Pattern: Agent per Module

```
# KHÔNG NÊN làm như này:
.claude/
├── agents/
│   ├── metadata-extractor-agent.md      ❌
│   ├── relationship-detector-agent.md   ❌
│   ├── validator-agent.md               ❌
│   ├── chunker-agent.md                 ❌
│   ├── ui-builder-agent.md              ❌
│   └── config-manager-agent.md          ❌
```

**Vấn đề:**
- Quá phức tạp để quản lý
- Agents overlap về expertise (tất cả đều Python AI)
- Khó maintain và update
- Confusing khi chọn agent nào

## ✅ Best Practice: Domain-Based Agents + Module-Based Skills

```
.claude/
├── agents/                              # 2-4 agents theo EXPERTISE
│   ├── python-ai-expert.md              # Core ML/AI development
│   └── vietnamese-nlp-expert.md         # Vietnamese-specific tasks
│
└── skills/                              # Skills theo MODULES/FEATURES
    ├── metadata-extraction.md           # Module: metadata_extractor_v3.py
    ├── relationship-detection.md        # Module: relationship logic
    ├── validation.md                    # Module: validator.py
    ├── chunking.md                      # Module: chunker.py
    ├── ui-components.md                 # Module: app.py, metadata_editor.py
    ├── vietnamese-patterns.md           # Shared: Vietnamese processing
    └── database-integration.md          # Shared: PostgreSQL/ChromaDB
```

## 🎭 Cách Organize cho Project của bạn:

### **Phân tích modules hiện tại:**

```python
your-project/
├── metadata_extractor_v3.py          # Core extraction logic
├── vietnamese_cleaner.py              # Vietnamese preprocessing
├── validator.py                       # Metadata validation
├── entity_extractor.py                # Entity extraction
├── prohibition_detector.py            # Prohibition detection
├── filename_generator.py              # Filename generation
├── structure_analyzer.py              # Document structure
├── text_extractor.py                  # Text extraction
├── chunker.py                         # Chunking logic
├── processor.py                       # Pipeline orchestration
├── collection_selector.py             # Collection selection
├── metadata_editor.py                 # UI: metadata editing
├── help_section.py                    # UI: help section
└── app.py                             # Main Streamlit app
```

### **Recommended Structure:**

```
.claude/
├── agents/
│   ├── python-ai-expert.md           # 80% of tasks
│   └── vietnamese-nlp-expert.md      # 20% specialized tasks
│
└── skills/
    ├── 01-project-overview.md        # High-level architecture
    │
    ├── 02-extraction-pipeline.md     # Covers:
    │                                  # - metadata_extractor_v3.py
    │                                  # - entity_extractor.py
    │                                  # - text_extractor.py
    │                                  # - structure_analyzer.py
    │
    ├── 03-vietnamese-processing.md   # Covers:
    │                                  # - vietnamese_cleaner.py
    │                                  # - Vietnamese patterns
    │                                  # - underthesea usage
    │
    ├── 04-validation-rules.md        # Covers:
    │                                  # - validator.py
    │                                  # - prohibition_detector.py
    │                                  # - Data quality checks
    │
    ├── 05-relationship-graph.md      # Covers:
    │                                  # - Relationship detection
    │                                  # - Graph traversal
    │                                  # - Parent-child logic
    │
    ├── 06-chunking-strategies.md     # Covers:
    │                                  # - chunker.py
    │                                  # - Manual chunking UI
    │                                  # - Semantic boundaries
    │
    ├── 07-ui-development.md          # Covers:
    │                                  # - app.py
    │                                  # - metadata_editor.py
    │                                  # - help_section.py
    │                                  # - Streamlit patterns
    │
    ├── 08-database-operations.md     # Covers:
    │                                  # - PostgreSQL schema
    │                                  # - ChromaDB integration
    │                                  # - BM25 indexing
    │
    └── 09-pipeline-orchestration.md  # Covers:
                                       # - processor.py
                                       # - collection_selector.py
                                       # - config_manager.py
                                       # - End-to-end workflow
```

## 📋 Skill File Organization Strategy:

### **Option A: Feature-Based (RECOMMENDED)**

Group related modules by **business feature**:

```markdown
# 02-extraction-pipeline.md

## Overview
This skill covers the complete metadata extraction pipeline including text extraction, structure analysis, entity recognition, and metadata enrichment.

## Modules Covered
- metadata_extractor_v3.py: Core extraction logic
- entity_extractor.py: Entity recognition
- text_extractor.py: Text extraction from PDFs
- structure_analyzer.py: Document structure analysis

## Core Patterns
[Include extraction patterns, algorithms, best practices]

## Code Examples
[Show how modules work together]

## Testing
[Tests for all extraction modules]
```

### **Option B: Layer-Based**

Group by **architectural layer**:

```
skills/
├── layer-1-data-ingestion.md        # text_extractor, file handling
├── layer-2-preprocessing.md         # vietnamese_cleaner, normalization
├── layer-3-extraction.md            # metadata_extractor, entity_extractor
├── layer-4-validation.md            # validator, prohibition_detector
├── layer-5-storage.md               # database operations
└── layer-6-presentation.md          # UI components
```

## 🚀 Usage Examples:

### **Scenario 1: Fix bug trong metadata_extractor_v3.py**

```bash
# Load relevant skills
claude-code \
  --agent python-ai-expert \
  --skill 01-project-overview \
  --skill 02-extraction-pipeline \
  --skill 03-vietnamese-processing

Prompt: "There's a bug in metadata_extractor_v3.py where legal 
document numbers aren't being extracted correctly. Help me debug."
```

**Why this works:**
- 1 agent có đủ AI/ML expertise
- 3 skills provide context:
  - Project overview: understand architecture
  - Extraction pipeline: understand the specific module
  - Vietnamese processing: understand language patterns

### **Scenario 2: Build new feature - Manual chunking UI**

```bash
claude-code \
  --agent python-ai-expert \
  --skill 01-project-overview \
  --skill 06-chunking-strategies \
  --skill 07-ui-development

Prompt: "Implement manual chunking UI where users can select 
semantic boundaries through Streamlit interface"
```

### **Scenario 3: Optimize relationship detection**

```bash
claude-code \
  --agent python-ai-expert \
  --skill 01-project-overview \
  --skill 05-relationship-graph \
  --skill 08-database-operations

Prompt: "Current relationship extraction is 40% accurate. 
Help me implement ML-based suggestions using embeddings"
```

### **Scenario 4: Add new Vietnamese document type**

```bash
claude-code \
  --agent vietnamese-nlp-expert \
  --skill 02-extraction-pipeline \
  --skill 03-vietnamese-processing \
  --skill 04-validation-rules

Prompt: "Add support for 'Công văn' document type with 
specific extraction patterns"
```

## 💡 Quy tắc "Golden Ratio":

### **Agents: 1-4 per project**
- **1 agent**: Small project, one domain
- **2 agents**: Medium project (general + specialist)
- **3-4 agents**: Large project (multiple expertise areas)
- **5+ agents**: ⚠️ Warning - probably over-engineering

### **Skills: 5-15 per project**
- **Under 5**: Might be too coarse-grained
- **5-10**: Sweet spot for most projects ✅
- **10-15**: Complex projects with many modules
- **Over 15**: ⚠️ Consider consolidation

## 🎯 Concrete Recommendation cho Vietnamese RAG:

### **Minimal Setup (Start Here):**

```
.claude/
├── agents/
│   └── python-ai-expert.md           # ONE agent
│
└── skills/
    ├── vietnamese-rag-overview.md    # Architecture & context
    ├── extraction-and-processing.md  # All extraction modules
    ├── ui-and-interaction.md         # All UI modules
    └── database-and-storage.md       # All DB modules
```

**Usage:** Single agent + load 1-2 relevant skills per task

### **Recommended Setup (Scalable):**

```
.claude/
├── agents/
│   ├── python-ai-expert.md           # General AI/ML tasks
│   └── vietnamese-nlp-expert.md      # Vietnamese-specific tasks
│
└── skills/
    ├── 01-project-overview.md        # Must-read context
    ├── 02-extraction-pipeline.md     # 5 extraction modules
    ├── 03-vietnamese-processing.md   # Vietnamese NLP
    ├── 04-validation-rules.md        # Validation modules
    ├── 05-relationship-graph.md      # Graph relationships
    ├── 06-chunking-strategies.md     # Chunking logic
    ├── 07-ui-development.md          # 3 UI modules
    ├── 08-database-operations.md     # PostgreSQL/ChromaDB
    └── 09-testing-strategies.md      # Testing approach
```

**Usage:** Choose appropriate agent + 2-3 relevant skills

### **Maximum Setup (Only if Team is Large):**

```
.claude/
├── agents/
│   ├── python-ai-expert.md           # ML/AI development
│   ├── vietnamese-nlp-expert.md      # Vietnamese NLP
│   ├── database-architect.md         # Database optimization
│   └── ui-ux-developer.md            # Streamlit development
│
└── skills/
    ├── [Same 9 skills as above]
```

## 📊 Decision Matrix:

| Your Need | Agents Strategy | Skills Strategy |
|-----------|-----------------|-----------------|
| Fix bug in specific module | 1 agent (python-ai-expert) | Load 2-3 related skills |
| Add new feature | 1 agent | Load feature + dependencies skills |
| Optimize performance | 1 agent | Load module + database skills |
| Vietnamese text issue | vietnamese-nlp-expert | Load vietnamese + extraction skills |
| Full pipeline refactor | python-ai-expert | Load overview + all relevant skills |

## ⚡ Pro Tips:

### **1. Start Minimal, Grow Organic**
```bash
# Week 1: Create basics
- python-ai-expert.md
- project-overview.md

# Week 2-3: Add as needed
- extraction-pipeline.md (when working on extraction)
- ui-development.md (when building UI)

# Week 4+: Refine based on usage patterns
```

### **2. Skills Should Cross-Reference**
```markdown
# In extraction-pipeline.md
See also:
- vietnamese-processing.md for text preprocessing
- validation-rules.md for output validation
- database-operations.md for storage
```

### **3. Keep Skills Focused but Complete**
```markdown
# Good: extraction-pipeline.md (covers 5 related modules)
✅ Focused on one business capability
✅ Includes all relevant modules
✅ Has code examples and tests

# Bad: metadata-extractor-only.md (covers 1 module)
❌ Too granular
❌ Missing context from related modules
❌ Hard to use effectively
```

### **4. Use Numbering for Dependency Order**
```
01-project-overview.md          # Start here
02-vietnamese-processing.md     # Foundation
03-extraction-pipeline.md       # Depends on #2
04-validation-rules.md          # Depends on #3
...
```

## 🎯 Final Answer:

**NO - Không cần agent riêng cho mỗi module.**

**Recommendation cho bạn:**
```
2 Agents:
├── python-ai-expert.md (80% công việc)
└── vietnamese-nlp-expert.md (20% Vietnamese-specific)

7-9 Skills (grouped by feature):
├── project-overview.md
├── extraction-pipeline.md (covers 5 extraction modules)
├── vietnamese-processing.md
├── validation-rules.md (covers 2 validation modules)
├── relationship-graph.md
├── ui-development.md (covers 3 UI modules)
├── database-operations.md
└── testing-strategies.md
```

**Why this works:**
- ✅ Simple to manage (2 agents vs 10 agents)
- ✅ Clear separation of concerns (expertise vs knowledge)
- ✅ Flexible combinations (2 agents × 9 skills = 18 possible combinations)
- ✅ Scalable (easy to add new skills for new modules)
- ✅ Maintainable (update skill without changing agent)

**Nguyên tắc vàng: Agents ít, Skills vừa phải, kết hợp linh hoạt!** 🎯
