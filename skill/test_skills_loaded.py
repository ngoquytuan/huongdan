#!/usr/bin/env python3
"""
Skill Verification Test for Claude Code
========================================

Run this script with Claude Code to verify all skills are loaded.

Usage:
    Ask Claude Code: "Hãy chạy file test_skills_loaded.py và trả lời tất cả questions"

Expected: Claude will answer all questions correctly if skills are loaded.
"""

import sys
from datetime import datetime

class SkillVerifier:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        self.skill_files = [
            "VIETNAMESE_GRAPH_RAG_SKILL.md",
            "data_ingestion_pipeline_skill.md",
            "embedding_model_selection_skill.md",
            "rag_retrieval_synthesis_generation_skill.md",
            "backend_complete_skills.md",
            "debugging_troubleshooting_skill.md",
            "MASTER_SKILLS_INDEX.md"
        ]
        
        self.verification_questions = [
            {
                "id": "Q1",
                "skill": "VIETNAMESE_GRAPH_RAG_SKILL.md",
                "question": "What are the 5 Vietnamese document types (patterns)?",
                "expected_keywords": ["LEGAL_RND", "HR_POLICY", "IT_MANUAL", "GEN_REPORT", "GENERAL"],
                "points": 10
            },
            {
                "id": "Q2",
                "skill": "VIETNAMESE_GRAPH_RAG_SKILL.md",
                "question": "What is the current metadata completeness rate mentioned in the skill?",
                "expected_keywords": ["92-95%", "92%", "95%"],
                "points": 10
            },
            {
                "id": "Q3",
                "skill": "data_ingestion_pipeline_skill.md",
                "question": "What is the maximum file upload size allowed?",
                "expected_keywords": ["100MB", "100 * 1024 * 1024", "100"],
                "points": 10
            },
            {
                "id": "Q4",
                "skill": "data_ingestion_pipeline_skill.md",
                "question": "What are the allowed file extensions for upload?",
                "expected_keywords": [".pdf", ".docx", ".txt", ".html", ".xlsx"],
                "points": 10
            },
            {
                "id": "Q5",
                "skill": "embedding_model_selection_skill.md",
                "question": "What is the default/recommended embedding model?",
                "expected_keywords": ["Qwen/Qwen3-Embedding-0.6B", "Qwen3", "1024"],
                "points": 10
            },
            {
                "id": "Q6",
                "skill": "embedding_model_selection_skill.md",
                "question": "What GPU is mentioned as the production hardware?",
                "expected_keywords": ["RTX 2080 Ti", "2080 Ti", "11GB"],
                "points": 10
            },
            {
                "id": "Q7",
                "skill": "rag_retrieval_synthesis_generation_skill.md",
                "question": "What are the 3 main components of the RAG pipeline?",
                "expected_keywords": ["Retrieval", "Synthesis", "Generation", "FR04.1", "FR04.2", "FR04.3"],
                "points": 10
            },
            {
                "id": "Q8",
                "skill": "rag_retrieval_synthesis_generation_skill.md",
                "question": "What is the RRF (Reciprocal Rank Fusion) constant value?",
                "expected_keywords": ["60", "1.0 / (60 + rank)"],
                "points": 10
            },
            {
                "id": "Q9",
                "skill": "backend_complete_skills.md",
                "question": "What are the 4 role levels in order (lowest to highest)?",
                "expected_keywords": ["Guest", "Employee", "Manager", "Director"],
                "points": 10
            },
            {
                "id": "Q10",
                "skill": "backend_complete_skills.md",
                "question": "What authentication method is used for the API?",
                "expected_keywords": ["JWT", "Bearer token", "HS256"],
                "points": 10
            },
            {
                "id": "Q11",
                "skill": "debugging_troubleshooting_skill.md",
                "question": "What function is used to debug file encoding issues?",
                "expected_keywords": ["debug_file_encoding", "chardet"],
                "points": 10
            },
            {
                "id": "Q12",
                "skill": "debugging_troubleshooting_skill.md",
                "question": "What is the recommended solution for CUDA out of memory error?",
                "expected_keywords": ["reduce batch size", "clear cache", "torch.cuda.empty_cache"],
                "points": 10
            },
            {
                "id": "Q13",
                "skill": "MASTER_SKILLS_INDEX.md",
                "question": "How many main skill files are there (excluding user-provided)?",
                "expected_keywords": ["6", "six"],
                "points": 10
            },
            {
                "id": "Q14",
                "skill": "data_ingestion_pipeline_skill.md",
                "question": "What task queue system is used for async processing?",
                "expected_keywords": ["Celery", "Redis", "celery worker"],
                "points": 10
            },
            {
                "id": "Q15",
                "skill": "backend_complete_skills.md",
                "question": "What monitoring tools are used in the stack?",
                "expected_keywords": ["Prometheus", "Grafana"],
                "points": 10
            }
        ]
    
    def print_header(self):
        print("\n" + "="*80)
        print(" " * 20 + "CLAUDE CODE SKILL VERIFICATION TEST")
        print("="*80)
        print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Questions: {len(self.verification_questions)}")
        print(f"Total Possible Points: {sum(q['points'] for q in self.verification_questions)}")
        print("\n" + "="*80)
    
    def print_skill_list(self):
        print("\n📚 EXPECTED SKILL FILES:")
        print("-" * 80)
        for i, skill in enumerate(self.skill_files, 1):
            print(f"  {i}. {skill}")
        print()
    
    def print_instructions(self):
        print("\n📋 INSTRUCTIONS FOR CLAUDE CODE:")
        print("-" * 80)
        print("""
This is a verification test to confirm all skill files are loaded.

IMPORTANT: Please answer EACH question below by:
1. Reading the specified skill file
2. Providing the EXACT answer from the skill
3. Including relevant quotes or code snippets where applicable

DO NOT give generic answers - cite the actual skill file content!

Grading:
- Full points: Answer matches expected keywords from skill
- Partial points: Correct concept but missing details
- Zero points: Generic answer or "I don't have access"

Let's begin! 🚀
        """)
        print("="*80)
    
    def print_questions(self):
        print("\n❓ VERIFICATION QUESTIONS:")
        print("="*80)
        
        for q in self.verification_questions:
            print(f"\n{q['id']} - [{q['points']} points]")
            print(f"📁 Skill File: {q['skill']}")
            print(f"❓ Question: {q['question']}")
            print(f"💡 Expected Keywords: {', '.join(q['expected_keywords'][:3])}...")
            print("-" * 80)
    
    def print_code_generation_test(self):
        print("\n" + "="*80)
        print("💻 CODE GENERATION TEST")
        print("="*80)
        print("""
Please generate a SHORT code snippet for ONE of the following:

Option 1: File upload validation (from data_ingestion_pipeline_skill.md)
Option 2: Hybrid retrieval function (from rag_retrieval_synthesis_generation_skill.md)
Option 3: JWT authentication decorator (from backend_complete_skills.md)

Requirements:
✅ Code must follow patterns from the skill file
✅ Include comments citing the skill
✅ Use same function/class names as in skill
✅ Include error handling as shown in skill

Points: 20
        """)
        print("="*80)
    
    def print_grading_rubric(self):
        print("\n" + "="*80)
        print("📊 GRADING RUBRIC")
        print("="*80)
        print("""
Question Scoring:
- 10 points: Perfect answer with skill citations
- 7-9 points: Correct but missing some details
- 4-6 points: Partially correct
- 1-3 points: Generic answer, no skill reference
- 0 points: Wrong or no answer

Code Generation Scoring:
- 20 points: Perfect - matches skill pattern exactly
- 15-19 points: Good - follows most patterns
- 10-14 points: Okay - some patterns missing
- 5-9 points: Poor - generic code, not from skill
- 0-4 points: Wrong or no code

Total Points Possible: 170

Grade Scale:
🏆 170-160 (94%+): EXCELLENT - All skills fully loaded
✅ 159-144 (85%+): GOOD - Skills loaded, minor issues
⚠️  143-119 (70%+): FAIR - Skills partially loaded
❌ <119 (70%-): FAIL - Skills not loaded properly

        """)
        print("="*80)
    
    def print_footer(self):
        print("\n" + "="*80)
        print("END OF VERIFICATION TEST")
        print("="*80)
        print("""
NEXT STEPS:

1. Claude Code should answer ALL questions above
2. Review answers against expected keywords
3. Check if code generation follows skill patterns
4. Calculate total score
5. Determine if skills are loaded properly

If score < 70%:
❌ Skills NOT loaded properly
   → Check skill file locations
   → Verify file format and encoding
   → Restart Claude Code session
   → See VERIFY_SKILLS_GUIDE.md for troubleshooting

If score >= 85%:
✅ Skills loaded successfully!
   → Ready to start development
   → Use MASTER_SKILLS_INDEX.md for navigation
   → Reference skills explicitly in prompts

        """)
        print("="*80)
        print("\nTest complete! Waiting for Claude Code responses...\n")
    
    def run_verification(self):
        """Main verification flow"""
        self.print_header()
        self.print_skill_list()
        self.print_instructions()
        self.print_questions()
        self.print_code_generation_test()
        self.print_grading_rubric()
        self.print_footer()

def main():
    """Run the skill verification test"""
    verifier = SkillVerifier()
    verifier.run_verification()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
