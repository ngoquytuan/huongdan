# Stack Profiling & Monitoring Techniques

## Overview

This guide covers runtime and compile-time techniques for measuring stack usage in bare metal STM32 applications.

---

## Method 1: Runtime Stack Watermarking (Production-Proven)

### Concept

Fill unused stack with known pattern at startup, then periodically scan to find high water mark.

```
Stack Memory Layout:
┌─────────────────┐ ← __initial_sp (top, high address)
│  Used Stack     │
│  (variables,    │
│   return addr,  │
│   saved regs)   │
├─────────────────┤ ← Current SP
│                 │
│  Painted with   │
│  0xA5A5A5A5     │
│  (unused)       │
│                 │
└─────────────────┘ ← Stack_Mem (bottom, low address)
```

### Complete Implementation

**File: stack_monitor.h**
```c
#ifndef STACK_MONITOR_H
#define STACK_MONITOR_H

#include <stdint.h>
#include <stddef.h>

// Declare symbols from startup assembly file
extern uint32_t Stack_Mem;      // Bottom of stack
extern uint32_t __initial_sp;   // Top of stack (initial SP)

/**
 * @brief Paint unused stack with pattern
 * @note Call once at startup, before main loop
 */
void StackPaint_MSP(void);

/**
 * @brief Measure stack high water mark
 * @return Number of bytes used (peak usage)
 */
size_t StackHighWaterBytes_MSP(void);

/**
 * @brief Get total stack size
 * @return Total stack size in bytes
 */
size_t StackSizeBytes(void);

/**
 * @brief Get stack usage percentage
 * @return Usage percentage (0-100)
 */
uint8_t StackUsagePercent(void);

#endif // STACK_MONITOR_H
```

**File: stack_monitor.c**
```c
#include "stack_monitor.h"
#include "stm32g4xx_hal.h"  // For __disable_irq, __enable_irq, __get_MSP

// Pattern to fill unused stack
#define STACK_PATTERN 0xA5A5A5A5u

// Helper functions to get stack boundaries
static inline uint32_t* stack_bottom(void) { 
    return &Stack_Mem; 
}

static inline uint32_t* stack_top(void) { 
    return &__initial_sp; 
}

/**
 * @brief Paint unused stack with pattern
 * @note Called at startup, fills from bottom to current SP
 */
void StackPaint_MSP(void)
{
    // Disable interrupts to prevent stack changes during painting
    __disable_irq();
    
    uint32_t *p = stack_bottom();
    uint32_t *limit = (uint32_t*)__get_MSP();  // Current stack pointer
    
    // Fill from bottom up to current SP
    while (p < limit) {
        *p++ = STACK_PATTERN;
    }
    
    __enable_irq();
}

/**
 * @brief Measure stack high water mark
 * @return Bytes used (from top down to first painted word)
 */
size_t StackHighWaterBytes_MSP(void)
{
    uint32_t *p = stack_bottom();
    uint32_t *top = stack_top();
    
    // Scan from bottom until we find modified (used) memory
    while (p < top && *p == STACK_PATTERN) {
        p++;
    }
    
    // Calculate used bytes from top down
    return (size_t)((uint8_t*)top - (uint8_t*)p);
}

/**
 * @brief Get total stack size
 */
size_t StackSizeBytes(void)
{
    return (size_t)((uint8_t*)stack_top() - (uint8_t*)stack_bottom());
}

/**
 * @brief Get stack usage percentage
 */
uint8_t StackUsagePercent(void)
{
    size_t used = StackHighWaterBytes_MSP();
    size_t total = StackSizeBytes();
    
    return (uint8_t)((used * 100) / total);
}
```

**File: startup_stm32g474xx.s (relevant excerpt)**
```asm
;*******************************************************************************
;* Stack Configuration
;*******************************************************************************

; Amount of memory (in bytes) allocated for Stack
Stack_Size      EQU     0x1000  ; 4KB stack (adjust as needed)

                AREA    STACK, NOINIT, READWRITE, ALIGN=3
Stack_Mem       SPACE   Stack_Size
__initial_sp

                EXPORT  Stack_Mem
                EXPORT  __initial_sp
```

### Integration with Main Loop

**File: main.c**
```c
#include "stack_monitor.h"
#include "debug_log.h"

// Global for SNMP export
uint16_t snmp_stack_usage = 0;

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    // ✅ CRITICAL: Paint stack at startup (before any deep calls)
    StackPaint_MSP();
    
    // Initialize peripherals
    MX_GPIO_Init();
    MX_UART_Init();
    // ... other init ...
    
    LOG_INFO("System", "Stack: %u bytes total", StackSizeBytes());
    
    uint32_t main_count = 0;
    
    while (1)
    {
        HAL_IWDG_Refresh(&hiwdg);
        slaveClockRun();  // Main application loop
        
        // ✅ Periodic stack monitoring (every 100 cycles)
        main_count++;
        if (main_count >= 100)
        {
            size_t used = StackHighWaterBytes_MSP();
            uint8_t percent = StackUsagePercent();
            
            LOG_DEBUG("Stack", "used=%u / %u (%u%%)", 
                used, StackSizeBytes(), percent);
            
            // Export to SNMP for remote monitoring
            snmp_stack_usage = (uint16_t)used;
            
            // ⚠️ Warning if usage exceeds 80%
            if (percent > 80) {
                LOG_WARN("Stack", "Usage critical: %u%%", percent);
            }
            
            main_count = 0;
        }
    }
}
```

### How It Works

**Timeline:**

```
T=0 (Startup):
  ┌─────────────────┐
  │  Unpainted      │ ← __initial_sp
  │  (random data)  │
  │                 │
  └─────────────────┘ ← Stack_Mem
  
  Call StackPaint_MSP():
  ┌─────────────────┐
  │  Used (0-100B)  │ ← Current SP
  ├─────────────────┤
  │  0xA5A5A5A5     │
  │  0xA5A5A5A5     │
  │  0xA5A5A5A5     │
  │  ...painted...  │
  └─────────────────┘ ← Stack_Mem

T=runtime (after deep calls):
  ┌─────────────────┐
  │  0x12345678     │ ← __initial_sp
  │  0xABCDEF00     │   (used stack)
  │  0x00112233     │
  ├─────────────────┤ ← Deepest SP reached
  │  0xA5A5A5A5     │
  │  0xA5A5A5A5     │   (still painted)
  │  ...unused...   │
  └─────────────────┘ ← Stack_Mem
  
  StackHighWaterBytes_MSP() scans from bottom,
  stops at first non-0xA5A5A5A5 value,
  calculates: top - scan_position = used bytes
```

### Advantages

✅ **Runtime measurement** (captures actual usage, not theoretical)  
✅ **Zero overhead** after initial paint (just RAM usage)  
✅ **Works with interrupts** (captures ISR stack usage too)  
✅ **Simple implementation** (no special tools required)  
✅ **Non-invasive** (doesn't affect timing)

### Limitations

⚠️ **One-time max** (shows peak, not current)  
⚠️ **Pattern collision** (if stack accidentally has 0xA5A5A5A5, reads as unused)  
⚠️ **Requires RAM** (pattern takes space)  
⚠️ **Must paint before deep calls** (paint at startup only)

---

## Method 2: GCC Stack Usage Analysis

### Compiler Flag: `-fstack-usage`

**In Makefile or project settings:**
```makefile
CFLAGS += -fstack-usage
```

**Generates `.su` files:**
```
main.c:45:main    128    static
gps.c:234:gps_once    256    static
slave_display.c:89:update_display    512    static,bounded
```

**Format:**
```
filename:line:function    bytes    qualifier
```

**Qualifiers:**
- `static` - Stack usage is deterministic
- `dynamic` - Stack usage varies (VLAs, alloca)
- `bounded` - Upper bound known but varies

### Analysis Script

```bash
#!/bin/bash
# analyze_stack_usage.sh

echo "=== Top 20 Stack Users ==="
find . -name "*.su" -exec cat {} \; | \
    grep -v "^#" | \
    sort -k2 -n -r | \
    head -20

echo ""
echo "=== Dynamic/Bounded Functions (High Risk) ==="
find . -name "*.su" -exec cat {} \; | \
    grep -E "dynamic|bounded" | \
    sort -k2 -n -r

echo ""
echo "=== Total Static Stack (Sum) ==="
find . -name "*.su" -exec cat {} \; | \
    grep "static" | \
    awk '{sum+=$2} END {print sum " bytes"}'
```

**Example output:**
```
=== Top 20 Stack Users ===
httpServer.c:145:generate_webpage    1536    static
gps.c:234:parse_nmea_full    512    static
slave_display.c:89:format_time_string    384    static
main.c:456:main_loop    256    static

=== Dynamic/Bounded Functions (High Risk) ===
ntpClient.c:89:process_ntp    384    bounded

=== Total Static Stack (Sum) ===
4832 bytes
```

### Interpreting Results

**Red flags (fix immediately):**
- Any `dynamic` qualifier → use fixed-size arrays
- Function > 512 bytes → move buffers to static/global
- `bounded` with large size → review logic

**Optimization targets:**
- Top 10 consumers → inline or reduce local vars
- Multiple 256-512 byte functions → candidates for inlining

---

## Method 3: Debugger Stack Pointer Monitoring

### Using Keil uVision

**Setup:**
```
1. Set breakpoint at function entry
2. View → Memory Windows → Memory 1
3. Enter address: &__initial_sp - stack_size
4. Run to breakpoint
5. View → Registers → SP (R13)
6. Calculate: stack_usage = __initial_sp - SP
```

**Automation with watchpoints:**
```
// In debugger console
watch SP < (__initial_sp - 3500)  // Trigger if SP drops below 500 bytes free
```

### Using GDB

```gdb
# Set breakpoint in deep function
break gps_once

# Run to breakpoint
run

# Print stack pointer
p/x $sp

# Calculate usage
p/d (__initial_sp - $sp)

# Continue and monitor
c
```

### Logic Analyzer / GPIO Toggle

For production debugging:

```c
void critical_function(void) {
    HAL_GPIO_WritePin(STACK_MON_GPIO, STACK_MON_PIN, GPIO_PIN_SET);
    
    size_t current_usage = __initial_sp - __get_MSP();
    if (current_usage > 3500) {  // <500 bytes free
        HAL_GPIO_WritePin(ALERT_GPIO, ALERT_PIN, GPIO_PIN_RESET);
    }
    
    // ... function logic ...
    
    HAL_GPIO_WritePin(STACK_MON_GPIO, STACK_MON_PIN, GPIO_PIN_RESET);
}
```

Monitor GPIO with logic analyzer to capture timing.

---

## Method 4: Linker Map File Analysis

### Generate Map File

**In Makefile:**
```makefile
LDFLAGS += -Wl,-Map=$(BUILD_DIR)/$(TARGET).map
```

**Analyze map file:**
```bash
grep -A 50 "Memory Configuration" project.map
```

**Example output:**
```
Memory Configuration

Name             Origin             Length             Attributes
RAM              0x20000000         0x00020000         xrw  (128KB)
FLASH            0x08000000         0x00080000         xr   (512KB)

Linker script and memory map

.stack          0x2001f000     0x1000
 Stack_Mem      0x2001f000     0x1000
 __initial_sp   0x20020000
```

### Calculate Available Stack

```
Total RAM: 0x20000 (128KB)
Stack Size: 0x1000 (4KB)
Stack Range: 0x2001f000 - 0x20020000

Safe Usage: 80% = 3276 bytes
Critical: 90% = 3686 bytes
```

---

## Method 5: Statistical Profiling with Timer

### Concept

Sample SP at regular intervals to build usage histogram.

```c
#define SAMPLE_BUFFER_SIZE 1000
uint32_t sp_samples[SAMPLE_BUFFER_SIZE];
uint16_t sample_index = 0;

void TIM6_DAC_IRQHandler(void)  // 1kHz timer
{
    if (__HAL_TIM_GET_FLAG(&htim6, TIM_FLAG_UPDATE))
    {
        __HAL_TIM_CLEAR_FLAG(&htim6, TIM_FLAG_UPDATE);
        
        if (sample_index < SAMPLE_BUFFER_SIZE) {
            sp_samples[sample_index++] = __get_MSP();
        }
    }
}

void analyze_sp_samples(void)
{
    uint32_t min_sp = 0xFFFFFFFF;
    uint32_t max_sp = 0;
    
    for (uint16_t i = 0; i < sample_index; i++) {
        if (sp_samples[i] < min_sp) min_sp = sp_samples[i];
        if (sp_samples[i] > max_sp) max_sp = sp_samples[i];
    }
    
    size_t max_usage = __initial_sp - min_sp;
    printf("Max stack usage: %u bytes\n", max_usage);
    
    // Build histogram
    // ... bin SP values and print distribution ...
}
```

### Advantages

✅ **Dynamic profiling** (captures timing-dependent behavior)  
✅ **Statistical view** (histogram shows typical vs peak)  
✅ **Interrupt-aware** (captures ISR stack usage)

### Limitations

⚠️ **Overhead** (timer ISR adds load)  
⚠️ **Memory** (samples buffer takes RAM)  
⚠️ **Sampling error** (may miss brief peaks)

---

## Comparison Matrix

| Method | Runtime | Overhead | Accuracy | Ease | ISR Aware |
|--------|---------|----------|----------|------|-----------|
| Watermarking | ✅ Yes | Zero | High | Easy | ✅ Yes |
| GCC -fstack-usage | ❌ No | Zero | Medium | Easy | ✅ Yes |
| Debugger | ✅ Yes | Zero | High | Hard | ⚠️ Partial |
| Map file | ❌ No | Zero | Low | Easy | ❌ No |
| Statistical | ✅ Yes | Medium | High | Medium | ✅ Yes |

**Recommendation:** Use watermarking for production, GCC analysis for development.

---

## Best Practices

### 1. Paint Early, Measure Often

```c
int main(void) {
    HAL_Init();
    
    // ✅ FIRST THING: Paint stack
    StackPaint_MSP();
    
    // Initialize everything
    SystemClock_Config();
    MX_GPIO_Init();
    // ...
    
    while (1) {
        // ✅ Monitor every second
        if (one_second_tick) {
            log_stack_usage();
        }
    }
}
```

### 2. Set Warning Thresholds

```c
#define STACK_WARN_PERCENT 80
#define STACK_CRIT_PERCENT 90

void monitor_stack(void) {
    uint8_t usage = StackUsagePercent();
    
    if (usage >= STACK_CRIT_PERCENT) {
        ERROR_HANDLER();  // Critical, may crash soon
    } else if (usage >= STACK_WARN_PERCENT) {
        LOG_WARN("Stack usage high: %u%%", usage);
    }
}
```

### 3. Export to Monitoring

```c
// SNMP OID for stack usage
uint16_t snmp_stack_usage_bytes = 0;
uint8_t snmp_stack_usage_percent = 0;

void update_snmp_stats(void) {
    snmp_stack_usage_bytes = (uint16_t)StackHighWaterBytes_MSP();
    snmp_stack_usage_percent = StackUsagePercent();
}
```

### 4. Combine Methods

```c
void comprehensive_stack_analysis(void) {
    // Method 1: Runtime watermarking
    size_t runtime_usage = StackHighWaterBytes_MSP();
    
    // Method 2: GCC analysis (from .su files)
    // Check build output: max static = 2800 bytes
    
    // Method 3: Debugger measurement
    // Breakpoint deepest function: SP = 0x2001F200
    // Usage = 0x20020000 - 0x2001F200 = 3584 bytes
    
    // Compare:
    printf("Runtime (watermark): %u\n", runtime_usage);
    printf("GCC static sum:      2800\n");
    printf("Debugger measured:   3584\n");
    
    // If watermark > GCC sum + 500: investigate ISR usage
    // If debugger > watermark: paint was done too late
}
```

---

## Troubleshooting

### Problem: Watermark Shows 100% Usage

**Causes:**
1. Stack overflow already occurred
2. Paint was done too late (after deep calls)
3. ISR triggered before paint completed

**Solution:**
```c
// Paint as FIRST action in main, before HAL_Init
int main(void) {
    StackPaint_MSP();  // ✅ Before anything else
    HAL_Init();
    // ...
}
```

### Problem: GCC Reports `dynamic` Stack

**Causes:**
```c
// Variable-length array
void bad_function(int n) {
    char buffer[n];  // ❌ Dynamic, unpredictable
}

// alloca
void also_bad(int size) {
    char *buf = alloca(size);  // ❌ Dynamic
}
```

**Solution:**
```c
#define MAX_BUFFER 256
void good_function(int n) {
    char buffer[MAX_BUFFER];  // ✅ Static, known size
    if (n > MAX_BUFFER) return;
    // ... use buffer ...
}
```

### Problem: Debugger and Watermark Disagree

**Debugger shows 3000 bytes, watermark shows 2500:**

**Cause:** Debugger measures at breakpoint (may not be deepest), watermark measures peak across entire run.

**Solution:** Trust watermark for production, use debugger for specific path analysis.

---

## Testing After Optimization

```c
void test_stack_optimization(void) {
    // 1. Baseline measurement
    StackPaint_MSP();
    run_full_system_test();
    size_t before = StackHighWaterBytes_MSP();
    
    // 2. Apply inline optimizations
    // ... rebuild with inlined functions ...
    
    // 3. Re-measure
    StackPaint_MSP();
    run_full_system_test();
    size_t after = StackHighWaterBytes_MSP();
    
    // 4. Verify savings
    if (after < before) {
        printf("✅ Stack reduced by %u bytes\n", before - after);
    } else {
        printf("❌ No improvement (before=%u, after=%u)\n", before, after);
    }
    
    // 5. Stress test (trigger deepest paths)
    trigger_gps_processing();
    trigger_ntp_sync();
    trigger_display_update();
    // ... measure again ...
}
```

---

## Summary Checklist

Before deploying stack optimization:

- [ ] Watermarking implemented and tested
- [ ] Baseline stack usage measured (runtime)
- [ ] GCC -fstack-usage analysis reviewed
- [ ] Top 10 stack consumers identified
- [ ] Warning thresholds configured (80%, 90%)
- [ ] SNMP/logging integration for monitoring
- [ ] After optimization: stack reduced by 10%+
- [ ] Stress tested with all features active
- [ ] No stack overflow crashes observed

---

## References

- ARM Cortex-M4 Generic User Guide (Stack operation)
- GCC Stack Usage Documentation
- STM32G4 Reference Manual (RM0440)
- Production code examples from GPS/NTP clock project