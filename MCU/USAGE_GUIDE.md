# HOW TO USE THE INLINE ANALYSIS PROMPTS

## 📦 Files Provided

You have been provided with multiple prompt options:

1. **READY_TO_USE_PROMPT.txt** - Full comprehensive analysis (Recommended)
2. **QUICK_PROMPT.txt** - Fast 10-minute scan
3. **PROMPT_INLINE_ANALYSIS.md** - Multiple prompt variations with explanations

---

## 🚀 QUICK START (5 Minutes)

### Step 1: Choose Your Prompt

**For first-time analysis** → Use `READY_TO_USE_PROMPT.txt`
**For quick check** → Use `QUICK_PROMPT.txt`
**For custom needs** → Browse `PROMPT_INLINE_ANALYSIS.md`

### Step 2: Copy the Prompt

Open the chosen file and copy **EVERYTHING** between the separator lines:
```
═══════════════════
COPY THIS SECTION
═══════════════════
```

### Step 3: Paste to Claude

1. Open a NEW conversation with Claude
2. Paste the entire prompt
3. Press Enter
4. Wait for analysis (2-5 minutes)

### Step 4: Review Results

Claude will provide:
- List of functions to inline
- Priority ranking
- Code examples (before/after)
- Stack savings calculations
- Implementation guide

---

## 📋 CHOOSING THE RIGHT PROMPT

### Use **READY_TO_USE_PROMPT.txt** when:
✅ First time analyzing your codebase
✅ Need comprehensive report with code examples
✅ Want detailed risk assessment
✅ Need implementation roadmap
✅ Have 10-15 minutes for analysis

**Output**: 
- Full report with ~10 candidates
- Complete before/after code
- Stack impact calculations
- Priority rankings
- Implementation steps

---

### Use **QUICK_PROMPT.txt** when:
✅ Need fast overview (< 5 minutes)
✅ Already know problem areas
✅ Just want top candidates
✅ Quick verification after changes

**Output**:
- Top 10 candidates only
- Brief metrics
- Priority tags
- Minimal code examples

---

### Use **PROMPT_INLINE_ANALYSIS.md** when:
✅ Need custom analysis
✅ Want to focus on specific files
✅ Have special constraints
✅ Need different output format

**Contains**:
- 4 different prompt variations
- Customization tips
- Advanced options
- Tool usage examples

---

## 🎯 EXPECTED OUTPUT EXAMPLES

### From READY_TO_USE_PROMPT.txt:

```markdown
## 🎯 Function: `stable_frac_offset()`

**📍 Location**: `gps.c:245`

**📊 Metrics**:
- Current Call Depth: 7 levels
- Function Size: 12 lines
- Stack Savings: 192 bytes

**🎚️ Priority**: 🔴 HIGH

**Implementation**:
[Complete before/after code]
```

### From QUICK_PROMPT.txt:

```markdown
Top 10 Inline Candidates:

1. stable_frac_offset() - gps.c:245
   Depth: 7, Size: 12 lines, Savings: 192 bytes
   Priority: HIGH
   
2. update_display() - slave_display.c:89
   Depth: 6, Size: 18 lines, Savings: 96 bytes
   Priority: MEDIUM
   
[... 8 more ...]
```

---

## ⚙️ CUSTOMIZING THE PROMPT

### Add More Context

Paste this **BEFORE** the main prompt:

```
Additional information for this analysis:

KNOWN ISSUES:
- Function X crashes when called from Y
- Webpage becomes unavailable intermittently

ALREADY ATTEMPTED:
- Inlined function A into B (successful)
- Increased stack from 1024 to 2048 bytes

CONSTRAINTS:
- Cannot modify HAL library functions
- Must preserve all LOG_DEBUG statements
- GPS timing accuracy must remain < 1ms
```

### Focus on Specific Files

Modify this section in the prompt:

```
## Step 1: Scan Source Files
Use the `view` tool to examine these critical files:
- `/mnt/project/YOUR_FILE_1.c`      ← Add your files here
- `/mnt/project/YOUR_FILE_2.c`
- `/mnt/project/YOUR_FILE_3.c`
```

### Change Priority Criteria

Modify this section:

```
### HIGH PRIORITY (Must inline):
- Call depth > 6 levels              ← Adjust threshold
- Function size < 15 lines           ← Adjust size limit
- Called in 1-2 places only          ← Adjust call count
```

---

## 🔍 INTERPRETING RESULTS

### Priority Levels

**🔴 HIGH (Do Immediately)**:
- High stack savings (> 100 bytes)
- Critical path functions
- Easy to implement
- Low risk

**🟡 MEDIUM (This Sprint)**:
- Moderate savings (50-100 bytes)
- Important functions
- Moderate effort
- Acceptable risk

**🟢 LOW (Optional)**:
- Small savings (< 50 bytes)
- Non-critical paths
- Higher effort
- Higher risk or code duplication

### Stack Savings

| Savings | Impact | Action |
|---------|--------|--------|
| > 150 bytes | 🔴 CRITICAL | Implement now |
| 100-150 | 🟠 HIGH | This week |
| 50-100 | 🟡 MEDIUM | This sprint |
| < 50 | 🟢 LOW | Optional |

### Risk Assessment

**Low Risk**:
- Function called once
- No complex logic
- Easy to test

**Medium Risk**:
- Called 2-3 places
- Some conditional logic
- Moderate testing

**High Risk**:
- Called > 3 places (code duplication)
- Complex logic
- Extensive testing needed

---

## 📝 AFTER GETTING RESULTS

### Step 1: Verify Recommendations
- Check if Claude identified correct call chains
- Verify stack savings calculations
- Review before/after code

### Step 2: Prioritize Implementation
Follow priority order:
1. HIGH priority first (biggest impact)
2. MEDIUM priority next
3. LOW priority last (if needed)

### Step 3: Implement Changes
For each function:
1. Copy the "AFTER" code
2. Test thoroughly
3. Verify stack usage improved
4. Commit with clear message

### Step 4: Validate
```c
// Add this to verify stack usage
void debug_stack(void) {
    uint32_t sp;
    __asm volatile ("MOV %0, SP" : "=r" (sp));
    printf("SP: 0x%08X\n", sp);
}
```

### Step 5: Re-analyze
After implementing changes:
- Run the prompt again
- Check for new opportunities
- Verify stack usage decreased

---

## 🆘 TROUBLESHOOTING

### "Claude didn't find any candidates"

**Possible reasons**:
1. Your code is already well optimized
2. Call chains are shallow (< 5 levels)
3. Functions are large (> 30 lines)

**Try**:
- Use QUICK_PROMPT.txt for overview
- Lower the thresholds in custom prompt
- Check specific problem areas manually

### "Too many candidates returned"

**Solution**:
- Focus on HIGH priority only
- Filter by stack savings > 100 bytes
- Look at top 5 candidates first

### "Code examples don't compile"

**Remember**:
- Claude generates examples, not final code
- You may need to adjust variable names
- Test thoroughly after implementation
- Preserve all functionality

### "Stack usage didn't improve"

**Check**:
- Did you inline the right functions?
- Are there other deep call chains?
- Did you test with same compiler optimization?
- Use stack monitoring to verify

---

## 💡 TIPS FOR BEST RESULTS

### Before Running Prompt:

1. **Clean up code first**
   - Remove unused functions
   - Fix obvious issues
   - Document known problems

2. **Prepare context**
   - List current issues
   - Note any attempted fixes
   - Identify critical paths

3. **Have metrics ready**
   - Current stack size
   - Peak stack usage
   - Problem scenarios

### During Analysis:

1. **Let Claude work**
   - Don't interrupt analysis
   - Wait for complete report
   - Claude may take 2-5 minutes

2. **Ask follow-up questions**
   ```
   "Can you show more detail for function X?"
   "What if I inline A and B together?"
   "Which order should I implement these?"
   ```

### After Analysis:

1. **Implement incrementally**
   - One function at a time
   - Test after each change
   - Monitor stack usage

2. **Document changes**
   ```c
   // REFACTORED 2026-01-21: Inlined stable_frac_offset()
   // Reason: Reduce call depth from 7 to 5 levels
   // Stack savings: 64 bytes
   ```

3. **Keep original code** (comment out)
   ```c
   #if 0  // Original code kept for reference
   void old_function(void) {
       // ...
   }
   #endif
   ```

---

## 📊 TRACKING YOUR PROGRESS

Create a simple spreadsheet:

| Function | Priority | Savings | Status | Date | Notes |
|----------|----------|---------|--------|------|-------|
| stable_frac_offset() | HIGH | 192B | ✅ Done | 01/21 | Works great |
| gps_once() | HIGH | 64B | 🔄 Testing | 01/21 | In progress |
| update_display() | MEDIUM | 48B | 📋 TODO | - | Next sprint |

**Goal**: Implement all HIGH priority first, achieve minimum 200 bytes savings.

---

## 🎓 LEARNING FROM RESULTS

After implementing recommendations:

### What Worked Well?
- Which functions were easy to inline?
- What was the actual stack savings?
- Any performance improvements?

### What Was Difficult?
- Which functions were hard to inline?
- Any unexpected issues?
- Testing challenges?

### Apply Learnings:
- Update your coding standards
- Train team on patterns
- Document best practices

---

## ✅ SUCCESS CHECKLIST

- [ ] Ran initial analysis with READY_TO_USE_PROMPT.txt
- [ ] Reviewed all HIGH priority candidates
- [ ] Implemented top 3 recommendations
- [ ] Tested thoroughly after each change
- [ ] Verified stack usage decreased
- [ ] Documented all changes
- [ ] Committed code with clear messages
- [ ] Re-ran analysis to verify improvement
- [ ] System runs stable for 24+ hours
- [ ] Updated team documentation

---

## 📞 NEXT STEPS

1. **Choose prompt** → READY_TO_USE_PROMPT.txt
2. **Copy & paste** to new Claude conversation
3. **Wait for results** (2-5 minutes)
4. **Review recommendations** 
5. **Implement HIGH priority** functions first
6. **Test thoroughly**
7. **Verify stack improvement**
8. **Repeat** if needed

---

**Remember**: Inline optimization is a tool, not a goal. Focus on reducing stack overflow risk while maintaining code quality.

Good luck! 🚀
