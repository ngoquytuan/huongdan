# STACK OVERFLOW PREVENTION - QUICK REFERENCE CARD
## Print this page and keep it visible during development

---

## 🎯 THE 3 GOLDEN QUESTIONS (Before Every Commit)

```
1. ✅ Any exact comparisons with interrupt counters?
2. ✅ Any shared variables missing 'volatile'?  
3. ✅ Any blocking operations in critical timing paths?
```

---

## 🛡️ THE 6 GOLDEN RULES (Never Violate)

| # | Rule | Limit | Why |
|---|------|-------|-----|
| 1 | **Call Depth** | Max 7 levels | Each level = 32 bytes overhead |
| 2 | **Local Arrays** | Max 128 bytes | Use `static` for larger buffers |
| 3 | **Printf Args** | Max 5 params | vsnprintf uses 128-256 bytes |
| 4 | **Recursion** | PROHIBITED | Unpredictable stack growth |
| 5 | **ISR Buffers** | ZERO local vars | ISRs share main stack |
| 6 | **Struct Passing** | By pointer if >16B | Avoid copying to stack |

---

## ⚠️ DANGER PATTERNS - AVOID THESE

```c
// ❌ BAD: Deep nesting + large buffers
void level1() {
    char buf[256];
    level2();  // Accumulates stack!
}

// ❌ BAD: Printf in deep call
void nested_function() {
    LOG_DEBUG("tag", "%d:%d:%d %s %d %d %d", ...);  // 8 args!
}

// ❌ BAD: Local buffer in ISR
void TIM3_IRQHandler() {
    char msg[64];  // ISR shares main stack!
    sprintf(msg, ...);
}
```

---

## ✅ SAFE PATTERNS - USE THESE

```c
// ✅ GOOD: Static buffer (not on stack)
void process() {
    static char buffer[512];  // In .bss section
    // ...
}

// ✅ GOOD: Flat call structure
void main_loop() {
    handle_gps();     // Direct calls
    handle_network(); // No deep nesting
    handle_display();
}

// ✅ GOOD: ISR sets flag only
void TIM3_IRQHandler() {
    flag = 1;  // Lightweight
    counter++;
}
```

---

## 📊 STACK SIZE GUIDELINES

| System Type | Minimum | Recommended |
|-------------|---------|-------------|
| Simple (GPIO/UART) | 1536 | 2048 |
| Medium (Network) | 2048 | 3072 |
| Complex (GPS+NTP+HTTP) | 3072 | 4096 |

**Safety Rule:** Stack usage should be < 70% during normal operation

---

## 🔍 CODE REVIEW CHECKLIST

### Function Review
- [ ] Call depth from main() < 7?
- [ ] No local arrays > 128 bytes?
- [ ] No printf with > 5 arguments?
- [ ] Structs passed by pointer?
- [ ] No recursion?

### ISR Review  
- [ ] Zero local variables?
- [ ] No function calls except HAL?
- [ ] No blocking operations?
- [ ] All shared vars `volatile`?

### System Review
- [ ] Stack size >= 2048 bytes?
- [ ] Stack monitoring enabled?
- [ ] Tested worst-case path?

---

## 🔧 EMERGENCY FIXES (When Stack Overflow Detected)

**Immediate (< 5 min):**
```c
// 1. Linker script: Double stack size
_Min_Stack_Size = 0x1000;

// 2. Comment out deepest calls temporarily
// deep_function();

// 3. Reduce printf arguments
// LOG("short", "%d", val);  // Instead of 10 args
```

**Short-term (< 1 hour):**
- Inline 2-3 deepest functions
- Convert local arrays to static
- Add stack monitoring code

---

## 📐 STACK CALCULATION FORMULA

```
Required Stack = Base + (Depth × 32) + Max_Locals + ISR_Margin

Example (your GPS/NTP system):
  Base:         512 bytes  (HAL, startup)
  Depth (7×32): 224 bytes  (call overhead)
  Max Local:    384 bytes  (buffers)
  ISR (20%):    224 bytes  (safety margin)
  ─────────────────────────
  Total:       1344 bytes
  Round up:    2048 bytes ✅ (safe)
```

---

## 🚨 WARNING SIGNS

**Healthy System:**
- Consistent behavior
- Stable operation
- No random resets

**Stack Problem Indicators:**
- ⚠️ "Works sometimes" 
- ⚠️ Webpage occasionally fails
- ⚠️ Variables randomly change
- ⚠️ Crashes in deep calls
- 🚨 Hard fault on function entry
- 🚨 Different behavior -O0 vs -O2

---

## 🔬 QUICK DEBUG COMMANDS

```c
// Check current stack usage
void debug_stack() {
    uint32_t sp;
    __asm volatile ("MOV %0, SP" : "=r" (sp));
    printf("SP: 0x%08X\n", sp);
}

// Add to critical functions
#define STACK_CHECK() do { \
    uint32_t sp; \
    __asm volatile ("MOV %0, SP" : "=r" (sp)); \
    if((sp - STACK_BASE) < 512) ERROR(); \
} while(0)
```

---

## 💡 REMEMBER

```
❌ "It works on my machine"        → Test with optimization -O2
❌ "It's just one more function"   → Check total depth!  
❌ "256 bytes is not much"         → On 2KB stack it's 12.5%!
❌ "I'll increase stack later"     → Do it NOW, RAM is cheap
✅ "Inline when in doubt"          → Reduces depth
✅ "Static for large buffers"      → Saves stack
✅ "Monitor in production"         → Catches issues early
```

---

## 🎯 THE ULTIMATE RULE

**When uncertain, always choose the safer option:**
- Inline instead of call
- Static instead of local  
- Main loop instead of ISR
- Bigger stack instead of smaller

**Stack overflow is silent, unpredictable, and catastrophic.**  
**Prevention is 100× easier than debugging.**

---

**Document Version:** 1.0 | **Date:** 2026-01-21  
**Project:** STM32 Bare Metal | **Target:** Production Deployment

---

*"The best stack overflow is the one that never happens."*
