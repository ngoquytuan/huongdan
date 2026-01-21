# STACK OVERFLOW PREVENTION RULES
## Embedded C Coding Standard for Bare Metal STM32

**Version:** 1.0  
**Date:** 2026-01-21  
**Target:** STM32 Bare Metal (No RTOS)  
**Author:** Embedded Systems Best Practices

---

## 📋 QUICK REFERENCE CARD

### The 3 Golden Questions (Ask Before Every Commit)
```
1. ✅ Any exact comparisons with interrupt counters?
2. ✅ Any shared variables missing 'volatile'?
3. ✅ Any blocking operations in critical timing paths?
```

### The Stack Safety Rule
```
Stack Usage = (Call Depth × 32) + Local Variables + Printf Buffers
Must be < 70% of total stack size
```

---

## 🛡️ PART 1: MANDATORY RULES (Never Violate)

### Rule #1: Function Call Depth Limit
**Maximum call depth: 7 levels**

```c
// ❌ BAD - 9 levels deep
main() → init() → setup() → config() → validate() 
     → check() → verify() → process() → execute()

// ✅ GOOD - 4 levels deep
main() → init() → setup() → process()
```

**Penalty:** Each level costs ~32 bytes stack overhead

---

### Rule #2: Local Array Size Limit
**Maximum local array: 128 bytes**

```c
// ❌ BAD - Stack eater
void process(void) {
    char buffer[512];     // 512 bytes on stack!
    uint32_t data[256];   // 1024 bytes on stack!
}

// ✅ GOOD - Use static
void process(void) {
    static char buffer[512];     // In .bss, not stack
    static uint32_t data[256];   // In .bss, not stack
}
```

**Rationale:** Local arrays accumulate through call chain

---

### Rule #3: Printf/Log Arguments Limit
**Maximum printf arguments: 5 parameters**

```c
// ❌ BAD - Internal buffer ~256 bytes
LOG_DEBUG("tag", "%d:%d:%d, %d-%d-%d, %d %c, offset %d ms, cnt %d",
          h, m, s, d, mo, y, sat, valid, offset, cnt);

// ✅ GOOD - Split into multiple logs
LOG_DEBUG("time", "%02d:%02d:%02d", h, m, s);
LOG_DEBUG("gps", "sat:%d offset:%dms", sat, offset/10);
```

**Cost:** vsnprintf() uses 128-256 byte internal buffer

---

### Rule #4: Recursion Ban
**Recursion is PROHIBITED**

```c
// ❌ BAD - Infinite stack growth
void recursive(int depth) {
    if(depth <= 0) return;
    char buf[64];  // 64 × depth = overflow!
    recursive(depth - 1);
}

// ✅ GOOD - Use iteration
void iterative(int max_depth) {
    static char buf[64];
    for(int i = 0; i < max_depth; i++) {
        // Process using same buffer
    }
}
```

**Reason:** Stack depth is unpredictable and uncontrollable

---

### Rule #5: ISR Restrictions
**Interrupt Service Routines: Zero local buffers**

```c
// ❌ BAD - Stack collision
void TIM3_IRQHandler(void) {
    char msg[64];  // Adds to main stack!
    sprintf(msg, "tick");
}

// ✅ GOOD - Flag only
void TIM3_IRQHandler(void) {
    tick_flag = 1;  // Set flag, process in main loop
    counter++;
}
```

**Critical:** ISRs share same stack as main code

---

### Rule #6: Struct Pass-by-Reference
**Always pass structs by pointer if > 16 bytes**

```c
typedef struct {
    uint32_t data[10];  // 40 bytes
} LargeStruct_t;

// ❌ BAD - 40 bytes copied to stack
void process(LargeStruct_t config) {
    // ...
}

// ✅ GOOD - 4 bytes pointer only
void process(const LargeStruct_t *config) {
    // ...
}
```

**Savings:** 36 bytes per call

---

## 🔍 PART 2: CODE REVIEW CHECKLIST

### Pre-Commit Checklist
```
Function Review:
[ ] Call depth from main() < 7 levels?
[ ] No local arrays > 128 bytes?
[ ] No printf/sprintf with > 5 args?
[ ] All structs passed by pointer?
[ ] No recursion?
[ ] No malloc() in time-critical code?

ISR Review:
[ ] Zero local variables in ISR?
[ ] No function calls except HAL_?
[ ] No blocking operations?
[ ] All shared vars declared volatile?

Memory Review:
[ ] Stack size >= 2048 bytes?
[ ] Stack monitoring enabled?
[ ] Tested with worst-case call chain?
```

---

### Function Complexity Score

Calculate for each function:
```
Complexity Score = (Call Depth × 10) 
                 + (Local Arrays KB × 100)
                 + (Printf Count × 20)

If Score > 200: REFACTOR REQUIRED
If Score > 150: WARNING - Review carefully
If Score < 100: GOOD
```

**Example:**
```c
void process_gps(void)  // Depth: 4, Arrays: 0.5KB, Printf: 2
{
    Score = (4 × 10) + (0.5 × 100) + (2 × 20)
          = 40 + 50 + 40
          = 130  ✅ ACCEPTABLE
}
```

---

## 📐 PART 3: SAFE PATTERNS

### Pattern #1: Static Buffer Reuse
```c
// Shared work buffer (not on stack)
static uint8_t g_work_buffer[512];

void function_A(void) {
    // Reuse global buffer
    memset(g_work_buffer, 0, sizeof(g_work_buffer));
    // ... use buffer ...
}

void function_B(void) {
    // Same buffer, different time
    memset(g_work_buffer, 0, sizeof(g_work_buffer));
    // ... use buffer ...
}
```

---

### Pattern #2: Flat Call Structure
```c
// ❌ BAD - Nested calls (depth 5)
void main(void) {
    level1();
}
void level1(void) { level2(); }
void level2(void) { level3(); }
void level3(void) { level4(); }
void level4(void) { /* work */ }

// ✅ GOOD - Flat structure (depth 2)
void main(void) {
    task1();
    task2();
    task3();
}
void task1(void) { /* work directly */ }
void task2(void) { /* work directly */ }
void task3(void) { /* work directly */ }
```

---

### Pattern #3: Defer Heavy Operations
```c
// In deep call chain - set flag only
void nested_function(void) {
    if(condition) {
        need_process_flag = 1;  // Lightweight
    }
}

// In main loop - do heavy work
void main_loop(void) {
    if(need_process_flag) {
        process_data();  // Printf, buffers, etc
        need_process_flag = 0;
    }
}
```

---

### Pattern #4: Compile-Time Array Size Check
```c
#define MAX_SAFE_LOCAL_ARRAY 128

#define DECLARE_LOCAL_ARRAY(type, name, size) \
    _Static_assert((size) <= MAX_SAFE_LOCAL_ARRAY, \
                   "Local array too large! Use static."); \
    type name[size]

// Usage:
void my_function(void) {
    DECLARE_LOCAL_ARRAY(char, buffer, 64);  // ✅ OK
    // DECLARE_LOCAL_ARRAY(char, big, 256); // ❌ Compile error!
}
```

---

## 🔧 PART 4: RUNTIME MONITORING

### Monitoring Strategy

**Level 1: Stack Canary (Essential)**
```c
#define CANARY_VALUE 0xDEADBEEF
volatile uint32_t stack_canary[16] = {CANARY_VALUE, ...};

void check_stack(void) {
    for(int i=0; i<16; i++) {
        if(stack_canary[i] != CANARY_VALUE) {
            ERROR_HANDLER();  // Stack overflow!
        }
    }
}
```

**Level 2: Stack Watermark (Development)**
```c
void init(void) {
    extern uint32_t _sstack;
    uint32_t *ptr = &_sstack;
    while(ptr < get_sp()) *ptr++ = 0xA5A5A5A5;
}

uint32_t get_max_usage(void) {
    // Count unpainted bytes
}
```

**Level 3: Real-Time Check (Critical Functions)**
```c
#define STACK_CHECK() do { \
    uint32_t sp; \
    __asm volatile ("MOV %0, SP" : "=r" (sp)); \
    if((sp - STACK_BASE) < 512) { \
        ERROR_HANDLER(); \
    } \
} while(0)

void critical_function(void) {
    STACK_CHECK();  // Auto-check at entry
    // ...
}
```

---

## 📊 PART 5: STACK SIZE CALCULATION

### Formula
```
Required Stack = Base + (Max Depth × 32) + Max Local Vars + ISR Margin

Where:
- Base:         512 bytes (HAL, startup)
- Max Depth:    Your deepest call chain × 32 bytes/frame
- Max Local:    Largest combined local variables
- ISR Margin:   20% extra for nested interrupts

Example (GPS/NTP system):
  Base:         512 bytes
  Depth (7×32): 224 bytes
  Max Local:    384 bytes (buffers)
  ISR (20%):    224 bytes
  ─────────────────────
  Required:    1344 bytes
  Rounded:     2048 bytes (safe)
```

---

### Stack Size Recommendations

| System Complexity | Minimum | Recommended | With Debug |
|-------------------|---------|-------------|------------|
| Simple (GPIO, UART) | 1024 | 1536 | 2048 |
| Medium (Network) | 1536 | 2048 | 3072 |
| Complex (GPS+NTP+HTTP) | 2048 | 3072 | 4096 |

**Rule of thumb:** Allocate 30-50% extra for safety margin

---

## 🚨 PART 6: WARNING SIGNS

### Runtime Indicators of Stack Problems

```
✅ Healthy System:
- Consistent behavior
- Stable webpage access
- Clean serial output
- No random resets

⚠️ Warning Signs:
- Intermittent failures
- "Works sometimes" behavior
- Webpage occasionally unavailable
- Variables randomly change
- Crashes in deep call chains

🚨 Critical Symptoms:
- Hard fault on function entry
- Corruption of global variables
- Watchdog resets during normal operation
- Different behavior with -O0 vs -O2
```

---

## 🎯 PART 7: QUICK FIXES

### Emergency Fixes (When Stack Overflow Detected)

**Immediate (< 5 minutes):**
```c
// 1. Increase stack size in linker script
_Min_Stack_Size = 0x1000;  /* Double current size */

// 2. Comment out deepest function calls
// function_level_7();  // Temporary disable

// 3. Reduce printf arguments
// LOG("%d:%d:%d", h,m,s);  // Instead of 10 args
```

**Short-term (< 1 hour):**
```c
// 1. Inline 2-3 deepest functions
// 2. Convert local arrays to static
// 3. Add stack monitoring
```

**Long-term (next sprint):**
```c
// 1. Refactor call structure
// 2. Implement proper logging framework
// 3. Add compile-time checks
```

---

## 📝 PART 8: PROJECT INTEGRATION

### Add to Project Setup

**1. Linker Script Configuration**
```ld
/* File: STM32xxx_FLASH.ld */
_Min_Stack_Size = 0x800;  /* 2048 bytes minimum */

/* Optional: Add stack guard region */
PROVIDE(_stack_guard_size = 256);
```

**2. Startup Code**
```c
/* In main() before while(1) */
Stack_Monitor_Init();
Memory_Analysis_Report();  // Print usage once
```

**3. Build Flags**
```makefile
# Makefile additions
CFLAGS += -fstack-usage        # Generate .su files
CFLAGS += -Wstack-usage=256    # Warn if function > 256 bytes
LDFLAGS += -Wl,-Map=output.map # Generate memory map
```

**4. CI/CD Checks**
```bash
# Pre-commit hook
#!/bin/bash
# Check for large local arrays
git diff --cached | grep -E "char\s+\w+\[([2-9][0-9]{2,}|[1-9][0-9]{3,})\]" && {
    echo "ERROR: Local array > 200 bytes detected!"
    exit 1
}
```

---

## 🔬 PART 9: DEBUGGING TECHNIQUES

### When Stack Overflow Suspected

**Step 1: Calculate Actual Usage**
```c
void debug_stack(void) {
    extern uint32_t _sstack, _estack;
    uint32_t sp;
    __asm volatile ("MOV %0, SP" : "=r" (sp));
    
    uint32_t size = &_estack - &_sstack;
    uint32_t used = &_estack - sp;
    uint32_t free = sp - &_sstack;
    
    printf("Stack: %u/%u used (%u%%), %u free\n",
           used, size, (used*100)/size, free);
}
```

**Step 2: Find Deepest Call**
```bash
# Parse .su files to find stack hogs
find . -name "*.su" -exec cat {} \; | \
    sort -k2 -n -r | head -20
```

**Step 3: Assembly Analysis**
```bash
# Check actual stack usage in assembly
arm-none-eabi-objdump -d firmware.elf | \
    grep -A 20 "my_function:" | \
    grep "sub.*sp"  # Look for stack allocation
```

---

## 📚 APPENDIX A: REFERENCE TABLE

### Stack Cost Reference

| Operation | Stack Cost | Notes |
|-----------|------------|-------|
| Function call | 4-32 bytes | Depends on register usage |
| Return address | 4 bytes | Automatic |
| Saved registers | 0-64 bytes | R4-R11, LR |
| Local char | 1-4 bytes | Aligned to 4 bytes |
| Local int/ptr | 4 bytes | 32-bit ARM |
| Local array[N] | N bytes | Aligned |
| Printf call | 128-512 bytes | vsnprintf buffer |
| ISR entry | +32 bytes | Added to main stack |

### Function Overhead Examples

```c
void minimal(void) { }           // ~8 bytes (just prologue/epilogue)
void small(int a) { return a; }  // ~12 bytes
void normal(void) {              // ~32 bytes
    int x, y;
    x = 10; y = 20;
}
void large(void) {               // ~300 bytes
    char buf[256];
    sprintf(buf, "test");
}
```

---

## 📚 APPENDIX B: AUTOMATED TOOLS

### Python Stack Analyzer
```python
#!/usr/bin/env python3
"""
Analyze .su files and warn about stack usage
Usage: python stack_check.py *.su
"""
import sys
import re

THRESHOLD = 256  # bytes

for filename in sys.argv[1:]:
    with open(filename) as f:
        for line in f:
            match = re.search(r'(\w+)\s+(\d+)', line)
            if match:
                func, size = match.groups()
                size = int(size)
                if size > THRESHOLD:
                    print(f"⚠️  {func}: {size} bytes "
                          f"(>{THRESHOLD} threshold)")
```

### Call Graph Generator
```bash
#!/bin/bash
# Generate call graph from source
cflow -d 10 *.c | \
    grep -v "^{" | \
    awk '{print NF-1, $0}' | \
    sort -rn | head -20
```

---

## 🎓 APPENDIX C: TRAINING CHECKLIST

### New Team Member Onboarding

```
Phase 1: Understanding (Day 1)
[ ] Read this document completely
[ ] Understand stack vs heap vs globals
[ ] Review actual system memory map
[ ] Run Memory_Analysis_Report()

Phase 2: Practice (Week 1)
[ ] Identify 3 functions violating rules
[ ] Refactor 1 deep call chain
[ ] Convert 3 local arrays to static
[ ] Add stack monitoring to 1 critical function

Phase 3: Mastery (Month 1)
[ ] Review all PRs for stack issues
[ ] Teach concepts to another team member
[ ] Add 1 improvement to this standard
[ ] Successfully detect stack bug in testing
```

---

## 📄 DOCUMENT REVISION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-21 | Initial release |
| | | Based on STM32G474 GPS/NTP project |
| | | Lessons learned from production issues |

---

## ✅ FINAL CHECKLIST: BEFORE PRODUCTION

```
System Design:
[ ] Stack size >= 2048 bytes
[ ] Maximum call depth documented
[ ] All critical paths profiled
[ ] Stack monitoring in place

Code Quality:
[ ] All rules enforced via code review
[ ] No rule violations in git history
[ ] Automated checks in CI/CD
[ ] Team trained on standards

Testing:
[ ] Stress tested for 24+ hours
[ ] Tested worst-case call chains
[ ] Tested with all interrupts enabled
[ ] Verified stack watermark < 70%

Documentation:
[ ] Architecture documented
[ ] Call graphs generated
[ ] Memory map documented
[ ] Stack analysis in README
```

---

**END OF STANDARD**

*Keep this document updated as project evolves.  
Review and update with each major refactoring.*

---

## 💡 QUICK REFERENCE SUMMARY

**The 3 Critical Questions:**
1. Exact comparison with interrupt counters?
2. Shared variables missing volatile?
3. Blocking operations in timing path?

**The 6 Golden Rules:**
1. Max call depth: 7 levels
2. Max local array: 128 bytes
3. Max printf args: 5 parameters
4. No recursion ever
5. Zero buffers in ISRs
6. Pass structs by pointer

**The Safety Formula:**
```
Stack Usage < 70% of Stack Size
Stack Size >= 2048 bytes
Monitoring = ENABLED
```

**When in Doubt:**
- Use static instead of local
- Inline instead of call
- Defer to main loop instead of process in ISR
