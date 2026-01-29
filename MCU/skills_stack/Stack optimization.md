---
name: stm32-stack-optimizer
description: Stack optimization and call depth analysis for bare metal STM32 systems. Use when debugging stack overflow, analyzing function call chains, identifying inline candidates, calculating stack savings, or optimizing memory usage in resource-constrained embedded systems (STM32G4, F4, H7). Triggers on "stack overflow", "reduce call depth", "inline functions", "optimize stack usage", or "memory constraints". Provides automated call graph analysis, structured inline recommendations with before/after code examples, and runtime stack profiling techniques.
---

# STM32 Stack Optimizer

Expert system for stack optimization in bare metal STM32 applications. Analyzes call depth, identifies inline candidates, calculates stack savings, and provides implementation-ready recommendations.

## When to Use This Skill

**Primary triggers:**
- Stack overflow crashes or hard faults
- Need to reduce function call depth
- Memory-constrained MCU (limited RAM)
- Optimizing for bare metal (no RTOS)
- Analyzing stack consumption
- Deciding which functions to inline

**Project characteristics:**
- STM32 microcontrollers (G4, F4, H7 series)
- Bare metal or minimal RTOS
- Stack size < 4KB (typical constraint)
- Deep call chains (>5 levels)
- Performance-critical timing paths

## Core Methodology

### Three-Step Workflow

**Step 1: Profile Current Stack Usage**

Use runtime stack watermarking:
```c
// See references/stack-profiling.md for complete implementation
StackPaint_MSP();  // Paint stack with pattern at startup
// ... run system ...
size_t used = StackHighWaterBytes_MSP();  // Measure high water mark
printf("Stack used: %u / %u bytes\n", used, StackSizeBytes());
```

**Step 2: Build Call Graph**

Automated analysis:
```bash
python3 scripts/analyze_call_depth.py /path/to/project
```

Manual analysis (if no script):
1. Start from `main()`
2. Trace function calls recursively
3. Mark depth level for each function
4. Identify deepest paths (>6 levels)

**Step 3: Identify Inline Candidates**

Use decision tree:
```
Function characteristics:
├─ Size < 30 lines?
│   ├─ YES ─> Call depth > 6?
│   │   ├─ YES ─> Called < 3 places?
│   │   │   ├─ YES ─> Priority: HIGH ✅
│   │   │   └─ NO ──> Priority: MEDIUM
│   │   └─ NO ──> Called < 3 places?
│   │       ├─ YES ─> Priority: MEDIUM
│   │       └─ NO ──> Priority: LOW
│   └─ NO ──> Keep as separate function ❌
```

## Quick Reference: Inline Criteria

### ✅ MUST INLINE (High Priority)

**Characteristics:**
- Call depth > 6 levels
- Function size < 15 lines
- Called in 1-2 places only
- Minimal local variables (< 32 bytes)
- In critical timing path (GPS, NTP, display)

**Example pattern:**
```c
// Current: 7-level deep chain
main() → system_loop() → clock_run() → one_second() 
  → gps_once() → stable_frac() → get_offset()

// After inlining get_offset() into stable_frac():
// Depth reduced to 6 levels, saves 32+ bytes
```

### 🟡 SHOULD INLINE (Medium Priority)

**Characteristics:**
- Call depth = 5-6 levels
- Function size < 25 lines
- Called in 2-3 places
- Local variables < 64 bytes
- Not in hot loop

### 🟢 CONSIDER INLINE (Low Priority)

**Characteristics:**
- Call depth = 4-5 levels
- Function size < 30 lines
- Called in 3-4 places
- Marginal stack savings (< 64 bytes)

### ❌ NEVER INLINE

**Do NOT inline if:**
- Function > 30 lines (code bloat)
- Called > 4 places (excessive duplication)
- Contains large buffers (>128 bytes local)
- Recursive or complex logic
- Used for debugging/testing isolation

## Stack Savings Calculation

### Formula

```
Stack Savings = (Eliminated Call Levels × Frame Overhead) 
              + Eliminated Local Variables
              - Code Size Increase (if called multiple times)

Where:
  Frame Overhead = 32 bytes (typical ARM Cortex-M)
  Local Variables = sum of all local vars in eliminated frames
```

### Example Calculation

**Before:**
```
Call chain: main() → A() → B() → C() → D()
Depth: 5 levels
Frame costs: 32 + 32 + 32 + 32 + 32 = 160 bytes
Local vars in D(): 8 bytes
Total: 168 bytes
```

**After inlining D() into C():**
```
Call chain: main() → A() → B() → C() [D inlined]
Depth: 4 levels
Frame costs: 32 + 32 + 32 + 32 = 128 bytes
Local vars: 8 bytes (same)
Total: 136 bytes

Savings: 168 - 136 = 32 bytes (19%)
```

## Implementation Pattern

### Standard Inline Template

**Before (separate function):**
```c
void parent_function(void) {
    int result;
    // ... setup code ...
    result = child_function(param1, param2);
    // ... use result ...
}

static int child_function(int a, int b) {
    int local_var = a + b;
    return local_var * 2;
}
```

**After (inlined):**
```c
void parent_function(void) {
    int result;
    // ... setup code ...
    
    // ✅ INLINED: child_function()
    {
        int local_var = param1 + param2;
        result = local_var * 2;
    }
    
    // ... use result ...
}

// ❌ REMOVED: child_function() - no longer needed
```

### Using GCC Attributes

**Force inline (high priority):**
```c
static inline __attribute__((always_inline)) 
int must_inline(int x) {
    return x * 2;
}
```

**Prevent inline (debugging):**
```c
__attribute__((noinline))
void keep_separate(void) {
    // Force compiler to NOT inline this
}
```

**Flatten call tree (aggressive):**
```c
__attribute__((flatten))
void critical_path(void) {
    // All called functions will be inlined
    helper1();
    helper2();
    helper3();
}
```

## Report Format

When analyzing, produce structured reports using this template:

```markdown
## 🎯 Function: `function_name()`

**📍 Location**: `file.c:line`

**📊 Metrics**:
- Current Call Depth: X levels
- Function Size: Y lines
- Local Variables: Z bytes
- Called From: N locations
- Stack Frame Cost: ~32 bytes

**🔗 Current Call Chain**:
main() → level1() → level2() → THIS()

**💾 Stack Impact**:
- Current: X bytes
- After inline: Y bytes
- **SAVINGS: Z bytes (P%)**

**🎚️ Priority**: HIGH / MEDIUM / LOW

**✅ Recommendation**: INLINE / KEEP SEPARATE

**📝 Rationale**:
1. [Reason based on criteria]
2. [Stack savings calculation]
3. [Code duplication assessment]
```

See `references/report-templates.md` for complete format.

## Workflow Integration

### In Main Loop

```c
void main(void) {
    HAL_Init();
    
    // ✅ Paint stack at startup
    StackPaint_MSP();
    
    while (1) {
        // Application logic
        slaveClockRun();
        
        // ✅ Periodic stack monitoring
        if (one_second_flag) {
            size_t used = StackHighWaterBytes_MSP();
            LOG_DEBUG("Stack: %u/%u bytes", used, StackSizeBytes());
            
            // ⚠️ Warning threshold (80%)
            if (used > (StackSizeBytes() * 80 / 100)) {
                LOG_WARN("Stack usage critical!");
            }
        }
    }
}
```

## Resources

This skill includes comprehensive guides and tools:

### References (Detailed Guides)

- **`references/call-depth-analysis.md`** - Build call graphs, identify deep paths
- **`references/inline-strategies.md`** - Complete criteria, patterns, tradeoffs
- **`references/stack-profiling.md`** - Runtime monitoring, GCC analysis tools
- **`references/report-templates.md`** - Structured output formats from todo_stack.txt

### Scripts (Automation)

- **`scripts/analyze_call_depth.py`** - Automated call graph analysis and inline candidate identification

### When to Load References

- **call-depth-analysis.md**: When building call graph manually or understanding methodology
- **inline-strategies.md**: When deciding whether to inline specific functions
- **stack-profiling.md**: When implementing runtime monitoring or analyzing GCC output
- **report-templates.md**: When generating formal analysis reports

## Common Patterns

### Pattern 1: GPS Timing Chain (High Priority)

**Problem:**
```c
// Deep chain: 7 levels
main() → system_loop() → clock_run() → one_second() 
  → gps_once() → stable_frac() → get_offset()
```

**Solution:**
```c
// Inline get_offset() and stable_frac()
// New depth: 5 levels, saves 64+ bytes
```

### Pattern 2: Display Update Chain

**Problem:**
```c
// Multiple small functions called frequently
display_update() → format_time() → pad_zeros() → display_char()
```

**Solution:**
```c
// Inline pad_zeros() and display_char() (< 10 lines each)
// Reduces call overhead by 64 bytes
```

### Pattern 3: Utility Functions

**Problem:**
```c
// Small helper called from many places
int clamp(int val, int min, int max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}
```

**Solution:**
```c
// Make inline with attribute
static inline int clamp(int val, int min, int max) {
    return (val < min) ? min : (val > max) ? max : val;
}
```

## Critical Constraints

**Must preserve:**
- All functionality and behavior (bit-identical output)
- GPS timing accuracy (sub-millisecond precision)
- Code readability (use meaningful names, comments)
- Debugging capability (add inline comments)

**Safety limits:**
- Max inline size: 30 lines per function
- Max code duplication: 4 call sites
- Max local vars: 128 bytes
- Test after each inline (not batch changes)

## Testing After Inline

**Required validation:**
1. ✅ Stack usage reduced (measure with StackHighWaterBytes_MSP)
2. ✅ Functionality preserved (bit-identical behavior)
3. ✅ No timing regressions (GPS PPS accuracy maintained)
4. ✅ Code size acceptable (Flash usage check)
5. ✅ Builds without warnings (verify -Wall -Wextra)

**Rollback if:**
- Stack savings < 32 bytes (not worth it)
- Code size increases > 10%
- Any functional regression
- Build time increases significantly

## Example Analysis Workflow

```bash
# Step 1: Profile current stack
# (Add stack monitoring code, run system, note usage)

# Step 2: Run automated analysis
python3 scripts/analyze_call_depth.py /mnt/project/

# Step 3: Review generated report
# - Top 10 inline candidates
# - Stack savings calculations
# - Implementation recommendations

# Step 4: Implement high-priority inlines
# - Start with deepest call chains
# - Inline one function at a time
# - Test after each change

# Step 5: Verify stack reduction
# (Re-run stack profiling, compare before/after)
```

## Success Criteria

**Target achievements:**
- Reduce max call depth by 2+ levels
- Save 200+ bytes stack (10%+ of total)
- Maintain 100% functional correctness
- Zero timing regressions
- Code size increase < 5%

## When NOT to Use This Skill

Skip this skill if:
- RTOS with dynamic task stacks (different optimization strategy)
- >16KB stack available (not constrained)
- No stack overflow symptoms
- Code uses `alloca()` or VLAs (variable length arrays)
- Performance is not critical (readability priority)