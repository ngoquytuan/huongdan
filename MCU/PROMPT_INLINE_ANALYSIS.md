# PROMPT: Analyze GPS Clock Source Code for Inline Refactoring Opportunities

---

## Copy and paste this prompt to Claude:

```
You are an embedded C expert specializing in stack optimization for bare metal STM32 systems.

PROJECT CONTEXT:
- Target: STM32G474 microcontroller (128KB RAM, 512KB Flash)
- Application: GPS/NTP synchronized clock with web interface
- Current issue: Stack overflow causing intermittent failures
- Stack size: 2048 bytes (needs optimization)
- No RTOS: Bare metal implementation

TASK:
Analyze the source code in /mnt/project/ directory and identify functions that should be refactored using inline optimization to reduce call depth and stack usage.

ANALYSIS CRITERIA:
1. Function size: Small functions (< 20 lines)
2. Call depth: Functions in deep call chains (depth > 5)
3. Local variables: Minimal local buffers
4. Call frequency: Called in 1-2 places only
5. Critical path: Functions in GPS/NTP timing critical paths

SPECIFIC FOCUS AREAS:
- GPS processing functions (gps.c, gps.h)
- Slave clock control (slaveControl.c, slave_*.c)
- Time synchronization functions
- Functions called from oneSecondfucns()
- Any functions in call chains > 6 levels deep

OUTPUT FORMAT:
For each function candidate, provide:

1. **Function Name**: `function_name()`
2. **Location**: File:Line
3. **Current Call Chain**: Show full call path
4. **Call Depth**: Number (e.g., 7 levels)
5. **Function Size**: Lines of code
6. **Local Variables**: Total bytes on stack
7. **Call Count**: How many places it's called
8. **Stack Savings**: Estimated bytes saved
9. **Priority**: HIGH/MEDIUM/LOW
10. **Recommendation**: Inline or keep separate
11. **Rationale**: Why inline this function
12. **Implementation**: Show before/after code

PRIORITY CALCULATION:
- HIGH: Depth > 6 AND Size < 15 lines AND Called 1-2 places
- MEDIUM: Depth > 5 OR Size < 20 lines
- LOW: Depth < 5 AND Called > 3 places

EXAMPLE OUTPUT:

---
## Function #1: stable_frac_offset()

**Location**: gps.c:245
**Current Call Chain**: 
```
main() → system_main_loop() → slaveClockRun() → oneSecondfucns() 
     → gps_once() → stable_frac_offset() [DEPTH: 7]
```

**Metrics**:
- Call Depth: 7 levels
- Function Size: 12 lines
- Local Variables: 4 bytes (int32_t)
- Called: 1 place (gps_once only)
- Stack Savings: ~64 bytes (removes 2 call frames)

**Priority**: 🔴 HIGH

**Recommendation**: ✅ INLINE into oneSecondfucns()

**Rationale**:
1. Deep call chain (7 levels) causing stack pressure
2. Small function (12 lines) - perfect for inline
3. Only called once - no code duplication
4. Critical timing path - inline improves performance
5. Saves 64 bytes stack (call frame overhead)

**Implementation**:

BEFORE:
```c
void oneSecondfucns(void) {
    if(gps_every_sec == 1) {
        gps_once();  // Calls stable_frac_offset() internally
    }
}

void gps_once(void) {
    stable_frac_offset();
    LOG_DEBUG(...);
    gps_every_sec = 0;
}

void stable_frac_offset(void) {
    if(slave_clock.work_mode != GPS_MODE) return;
    DELTA_PPS_GPS_RTC = check_PPS_GPS;
    // ... logic ...
}
```

AFTER:
```c
void oneSecondfucns(void) {
    if(gps_every_sec == 1) {
        // ✅ INLINED stable_frac_offset() + gps_once() logic
        if(slave_clock.work_mode == GPS_MODE) {
            DELTA_PPS_GPS_RTC = check_PPS_GPS;
            // ... inlined logic ...
        }
        LOG_DEBUG(...);  // Simplified
        gps_every_sec = 0;
    }
}

// ❌ Remove gps_once() and stable_frac_offset()
```

**Stack Impact**:
- Before: 7 levels × 32 bytes = 224 bytes overhead
- After: 5 levels × 32 bytes = 160 bytes overhead
- **SAVINGS: 64 bytes (28% reduction)**

---

DELIVERABLES:
1. Complete list of inline candidates (sorted by priority)
2. Total potential stack savings
3. Recommended refactoring order
4. Risk assessment for each change
5. Code examples for top 5 candidates

CONSTRAINTS:
- Do NOT inline functions called > 3 places (code bloat)
- Do NOT inline functions > 30 lines (maintainability)
- Do NOT inline functions with large local buffers
- PRESERVE original logic and behavior
- MAINTAIN code readability

BEGIN ANALYSIS NOW.
Scan /mnt/project/ directory and provide comprehensive inline refactoring report.
```

---

## Alternative Shorter Prompt (Quick Analysis):

```
Analyze the GPS clock source code in /mnt/project/ and identify functions that should be inlined to reduce stack overflow risk.

Focus on:
1. Functions in call chains > 5 levels deep
2. Small functions (< 20 lines)
3. Called in only 1-2 places
4. GPS/NTP timing critical paths

For each candidate, report:
- Function name and location
- Current call depth
- Stack savings if inlined
- Priority (HIGH/MEDIUM/LOW)
- Before/after code example

Sort by priority and show top 10 candidates.
```

---

## Focused Prompt (Specific Function Analysis):

```
I have a GPS clock system on STM32G474 with stack overflow issues.

Analyze these specific function call chains and recommend which functions to inline:

1. Main timing chain:
   main() → system_main_loop() → slaveClockRun() → oneSecondfucns() → gps_once() → stable_frac_offset()

2. Display chain:
   main() → system_main_loop() → slaveClockRun() → display_update() → [sub-functions]

3. Network chain:
   main() → system_main_loop() → network_process() → [sub-functions]

For each chain:
- Calculate current stack depth
- Identify inline candidates
- Show estimated stack savings
- Provide refactored code examples
- Assess risk vs benefit

Project files are in /mnt/project/
```

---

## Advanced Prompt (With Tool Usage):

```
You are an embedded systems expert. I need a comprehensive stack optimization analysis.

STEP 1: SCAN SOURCE CODE
Use project_knowledge_search and view tools to scan:
- /mnt/project/gps.c
- /mnt/project/gps.h  
- /mnt/project/slaveControl.c
- /mnt/project/slave_*.c files
- /mnt/project/main.c

STEP 2: BUILD CALL GRAPH
Map all function calls starting from main() to identify:
- Maximum call depth
- Critical paths (GPS, NTP, network)
- Functions called in deep chains

STEP 3: IDENTIFY INLINE CANDIDATES
Find functions matching:
- Call depth > 5
- Function size < 25 lines
- Called 1-2 times
- Minimal local variables (< 64 bytes)

STEP 4: CALCULATE IMPACT
For each candidate:
- Current stack usage
- Stack savings if inlined
- Code size impact
- Maintainability score

STEP 5: PRIORITIZE
Rank by:
1. Stack savings potential
2. Implementation difficulty  
3. Risk level

STEP 6: GENERATE REPORT
Format:
```
# INLINE REFACTORING ANALYSIS REPORT
## GPS Clock System - STM32G474

### Executive Summary
- Total functions analyzed: X
- Inline candidates found: Y
- Total stack savings potential: Z bytes

### Priority 1 (Implement Immediately)
[List with code examples]

### Priority 2 (Next Sprint)
[List with code examples]

### Priority 3 (Optional)
[List with code examples]

### Risk Assessment
[Analysis of potential issues]

### Implementation Guide
[Step-by-step refactoring instructions]
```

BEGIN ANALYSIS NOW.
```

---

## Usage Instructions:

1. **Choose the appropriate prompt** based on your needs:
   - Full analysis: Use first prompt
   - Quick scan: Use second prompt
   - Specific chains: Use third prompt
   - Comprehensive: Use fourth prompt

2. **Copy the prompt** to Claude

3. **Claude will**:
   - Scan your source files
   - Build call graphs
   - Identify inline candidates
   - Calculate stack savings
   - Provide code examples
   - Generate priority list

4. **You get**:
   - Detailed report
   - Before/after code
   - Stack impact analysis
   - Implementation guidance

---

## Tips for Best Results:

**Add Context**:
```
Additional context:
- Stack size: 2048 bytes
- Current peak usage: ~40%
- Problem functions: gps_once(), stable_frac_offset()
- Already inlined: [list if any]
```

**Specify Constraints**:
```
Constraints:
- Must maintain GPS timing accuracy (sub-millisecond)
- Cannot modify HAL functions
- Preserve all LOG_DEBUG for debugging
- Code must remain readable
```

**Request Specific Format**:
```
Output format preference:
- Markdown tables for comparison
- Code blocks with syntax highlighting
- Stack usage diagrams (ASCII art)
- Priority color coding
```

---
