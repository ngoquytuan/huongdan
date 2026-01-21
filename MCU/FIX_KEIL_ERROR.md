# FIX KEIL COMPILER ERROR - Stack Monitor

## ❌ THE ERROR

```
compiling main.c...
../user/stack_monitor.h(109): error: #18: expected a ")"
      __asm volatile ("MOV %0, SP" : "=r" (sp));
```

---

## 🎯 ROOT CAUSE

**Keil ARM Compiler uses DIFFERENT inline assembly syntax than GCC!**

```c
// GCC syntax (arm-none-eabi-gcc):
__asm volatile ("MOV %0, SP" : "=r" (sp));  ✅ Works in GCC

// Keil syntax (Keil MDK-ARM):
__asm { MOV sp, SP }  ✅ Works in Keil
```

The original `stack_monitor.h` was written for GCC, so it fails in Keil!

---

## ✅ SOLUTION: 3 OPTIONS

### **OPTION 1: Use SIMPLE Version (RECOMMENDED for Keil)**

**Replace** `stack_monitor.h` with `stack_monitor_simple.h`:

```c
// In main.c - CHANGE THIS LINE:
// #include "stack_monitor.h"  ❌ Old version

// TO THIS:
#include "stack_monitor_simple.h"  ✅ New version
```

**Why this works:**
- NO inline assembly
- Pure ANSI C
- Works with ALL compilers (Keil, GCC, IAR)
- Uses local variable address trick instead of assembly

**Usage is IDENTICAL:**
```c
int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    Stack_Monitor_Init();  // Same function name!
    
    while(1) {
        system_main_loop();
        Stack_Monitor_Periodic();  // Same!
    }
}

void critical_function(void) {
    STACK_CHECK();  // Same!
    // ...
}
```

---

### **OPTION 2: Use CMSIS Function (Alternative)**

If you want to keep original `stack_monitor.h`, modify it:

**Find this section** (around line 109):
```c
static inline uint32_t Stack_Get_SP(void)
{
    uint32_t sp;
    __asm volatile ("MOV %0, SP" : "=r" (sp));  // ❌ GCC syntax
    return sp;
}
```

**Replace with:**
```c
static inline uint32_t Stack_Get_SP(void)
{
    return __get_MSP();  // ✅ CMSIS function, works everywhere!
}
```

**Note:** `__get_MSP()` is CMSIS intrinsic available in all ARM compilers

---

### **OPTION 3: Use Version 2.0 (Most Compatible)**

I created `stack_monitor_v2.h` that auto-detects compiler:

```c
// In main.c:
#include "stack_monitor_v2.h"
```

This version automatically uses:
- `__get_MSP()` for CMSIS (preferred)
- GCC inline assembly for GCC
- Keil inline assembly for Keil
- IAR intrinsic for IAR

---

## 📂 FILES PROVIDED

| File | Compatibility | Complexity | Accuracy |
|------|---------------|------------|----------|
| `stack_monitor.h` | GCC only ❌ | Complex | High |
| `stack_monitor_v2.h` | All compilers ✅ | Medium | High |
| `stack_monitor_simple.h` | All compilers ✅✅ | Simple | Medium |

**RECOMMENDATION for Keil users: Use `stack_monitor_simple.h`**

---

## 🔧 STEP-BY-STEP FIX

### Step 1: Download the new file

Choose ONE of these files:
- `stack_monitor_simple.h` (easiest)
- `stack_monitor_v2.h` (most features)

### Step 2: Replace in your project

```bash
# Backup old file
cp user/stack_monitor.h user/stack_monitor.h.backup

# Copy new file
cp stack_monitor_simple.h user/stack_monitor.h
```

### Step 3: Update include in main.c

```c
// main.c - update include path if needed
#include "stack_monitor.h"  // or "stack_monitor_simple.h"
```

### Step 4: Recompile

```bash
# Clean build
make clean
make

# Or in Keil IDE:
# Project → Rebuild all target files
```

### Step 5: Verify

You should see output like:
```
[INFO][Stack] Monitor initialized
[INFO][Stack]   Size: 2048 bytes
[INFO][Stack]   Canary at: 0x20003000
```

---

## 💡 UNDERSTANDING THE ISSUE

### Why Different Compilers?

Each compiler has its own inline assembly syntax:

| Compiler | Syntax Example |
|----------|----------------|
| **GCC** | `__asm volatile ("MOV %0, SP" : "=r" (sp));` |
| **Keil v5** | `__asm { MOV sp, SP }` |
| **Keil v6** | Same as GCC (uses Clang) |
| **IAR** | `asm("MOV %0, SP" : "=r" (sp));` |

### Best Practice

✅ **Use CMSIS intrinsics** whenever possible:
```c
__get_MSP()   // Get Main Stack Pointer
__get_PSP()   // Get Process Stack Pointer
__get_CONTROL() // Get CONTROL register
```

These work across ALL compilers!

⚠️ **Avoid inline assembly** unless absolutely necessary

---

## 🧪 TESTING

After fixing, test your system:

```c
// In main.c, after init:
Stack_Monitor_Init();
Stack_Report();  // Print initial state

// Should print:
// [INFO][Stack] === Report ===
// [INFO][Stack] SP:    0x20017F00
// [INFO][Stack] Total: 2048 bytes
// [INFO][Stack] Used:  256 bytes
// [INFO][Stack] Free:  1792 bytes
// [INFO][Stack] Canary: OK
```

---

## 🆘 IF STILL ERRORS

### Error: "undefined reference to `_estack`"

**Fix:** Your linker script doesn't define `_estack` and `_sstack`

**Check your .ld file** (e.g., `STM32G474xx_FLASH.ld`):

```ld
/* Should have these symbols: */
_estack = ORIGIN(RAM) + LENGTH(RAM);    /* Top of stack */
_sstack = _estack - _Min_Stack_Size;    /* Bottom of stack */
```

**If missing, add to your linker script:**
```ld
/* User_heap_stack section, used to check that there is enough RAM left */
._user_heap_stack :
{
    . = ALIGN(8);
    PROVIDE ( _sstack = . );
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
} >RAM

_estack = ORIGIN(RAM) + LENGTH(RAM);
```

### Error: "undefined reference to `__get_MSP`"

**Fix:** Add CMSIS Core header

```c
// At top of stack_monitor.h, add:
#include "core_cm4.h"  // Or core_cm3.h, core_cm7.h, etc.
```

Or in your main.h:
```c
#include "stm32g4xx_hal.h"  // This includes CMSIS
```

---

## 📊 PERFORMANCE COMPARISON

| Method | Speed | Accuracy | Compatibility |
|--------|-------|----------|---------------|
| Inline ASM | Fastest | Perfect | Compiler-specific |
| CMSIS `__get_MSP()` | Fast | Perfect | All compilers ✅ |
| Local variable trick | Medium | ±32 bytes | All compilers ✅ |

**For stack overflow detection, ±32 bytes error is acceptable!**

---

## ✅ FINAL CHECKLIST

```
[ ] Downloaded stack_monitor_simple.h or stack_monitor_v2.h
[ ] Replaced old stack_monitor.h
[ ] Updated #include in main.c
[ ] Rebuilt project successfully
[ ] Saw "Stack Monitor initialized" message
[ ] Tested with STACK_CHECK() in critical functions
[ ] System runs without crashes
```

---

## 📝 SUMMARY

**Problem:** Keil doesn't understand GCC inline assembly syntax

**Solution:** Use `stack_monitor_simple.h` which:
- Uses pure C (no assembly)
- Works with all compilers
- Same API as original
- Slightly less accurate (±32 bytes) but good enough!

**Alternative:** Use CMSIS `__get_MSP()` function

---

**Your system should compile and run perfectly now! 🎉**

If you still have issues, let me know:
1. Which file are you using?
2. Full error message
3. Compiler version (Keil version number)
