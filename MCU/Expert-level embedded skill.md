---
name: embedded-c-debug
description: Expert-level embedded C programming for STM32 microcontrollers with focus on real-time systems, GPS/NTP time synchronization, and interrupt-driven architectures. Use this skill when working on STM32 projects involving precise timing (sub-millisecond accuracy), multi-source time synchronization (GPS, NTP, RTC), interrupt handlers, race conditions, stack overflow issues, or network security (UDP spoofing). Specifically triggers for code review, debugging timing issues, validating NMEA/NTP protocols, and preventing embedded systems vulnerabilities like race conditions and deadlocks.
---

# Embedded C Programming & Debug Expert

This skill provides systematic code review, debugging workflows, and automated scanning for embedded C projects, with expertise in STM32 real-time timing systems.

## Core Review Methodology

### The Three Golden Questions

**ALWAYS ask these questions first when reviewing embedded code:**

1. **Exact comparison with interrupt counters?**
   - Search for: `if (counter == value)` with interrupt-modified variables
   - Fix: Use range comparison `if (counter >= value)`

2. **Shared variables missing volatile?**
   - Check all variables accessed by ISR and main loop
   - Fix: Add `volatile` keyword

3. **Blocking operations in critical paths?**
   - Look for: I2C/SPI calls, printf(), HAL_Delay() in ISRs
   - Fix: Move to non-blocking or defer to main loop

### Systematic Review Workflow

**Step 1: Automated Scan**
```bash
# Run the embedded code scanner
python3 scripts/audit_embedded_c.py <path_to_source>
```

**Step 2: Manual Deep Dive**
Priority order for manual review:
1. All ISR handlers (EXTI, Timer, UART, DMA callbacks)
2. Time-critical functions (GPS/PPS processing, NTP sync)
3. Shared data structures between ISR and main
4. String operations and buffer handling
5. Network packet validation
6. Main loop state machines

**Step 3: Reference Checklists**
Load detailed checklists as needed:
- `references/race-conditions.md` - Interrupt safety patterns
- `references/stack-overflow.md` - Stack usage detection
- `references/timing-validation.md` - GPS/NTP timing rules
- `references/network-security.md` - UDP/NTP packet validation
- `references/common-bugs.md` - Known embedded pitfalls

## Quick Patterns Reference

### Race Condition Prevention
```c
// ❌ WRONG - Race condition
uint32_t shared_counter;
void ISR() { shared_counter++; }
void main() { if (shared_counter == 100) {...} }

// ✅ CORRECT
volatile uint32_t shared_counter;
void main() { 
    uint32_t local = shared_counter;  // Atomic snapshot
    if (local >= 100) {...}           // Range comparison
}
```

### Atomic Data Access
```c
// For multi-byte structs accessed by ISR
typedef struct {
    uint32_t timestamp;
    uint16_t fraction;
    uint8_t valid;
} TimeData;

volatile TimeData gps_time;

// ✅ CORRECT - Atomic copy
void main() {
    TimeData snapshot;
    __disable_irq();
    snapshot = gps_time;
    __enable_irq();
    // Use snapshot safely
}
```

### Stack Overflow Prevention
```c
// ❌ DANGEROUS - Large local arrays
void bad_function() {
    char buffer[512];  // Stack overflow risk!
}

// ✅ BETTER - Static or global
static char buffer[512];  // Or allocate globally
void safe_function() {
    // Use shared buffer
}
```

## STM32 Timing System Specifics

### PPS Interrupt Handling
```c
// PPS on rising edge (PB9)
// TIM1->CNT as fractionOfSecond (0-9999)
void EXTI9_5_IRQHandler(void) {
    if (EXTI->PR & EXTI_PR_PR9) {
        EXTI->PR = EXTI_PR_PR9;  // Clear flag
        
        // ✅ CORRECT: Read at exact PPS edge
        volatile uint32_t pps_snapshot = TIM1->CNT;
        
        // ✅ Set flag for main loop processing
        pps_flag = 1;
        
        // ❌ NEVER: I2C/printf/blocking ops here!
    }
}
```

### GPS vs NTP Timing Offset
```c
// GPS PPS edge-triggered: Add +1 second
if (time_source == GPS) {
    rtc_time.second = gps_second + 1;
}

// NTP level-based: No offset
if (time_source == NTP) {
    rtc_time.second = ntp_second;  // Already correct
}
```

## Project Context Integration

This skill is optimized for projects with:
- **MCU**: STM32G4xx series (128MHz, limited stack)
- **GPS**: LEA-M8F with PPS output
- **Network**: W5500 Ethernet controller
- **RTC**: DS3231 high-precision external RTC
- **Displays**: MAX7219 LED drivers, 7-segment displays
- **Protocols**: NMEA parsing, NTP client/server, SNMP monitoring

## Debug Logging Standards

Always use structured debug logging:
```c
#include "debug_log.h"

// Timing-critical events
DEBUG_LOG("[GPS] PPS detected, fraction=%lu, valid=%c", 
    TIM1->CNT, gps_data.valid);

// State transitions
DEBUG_LOG("[SYNC] Source changed: %s -> %s", 
    old_source_name, new_source_name);

// Error conditions
DEBUG_LOG("[ERROR] NTP timeout after %d retries", retry_count);
```

## When NOT to Use This Skill

- General C programming without embedded constraints
- Arduino/ESP32 projects (different toolchain)
- Linux userspace applications
- Python/JavaScript projects
- Non-real-time systems

## Validation Before Deployment

Run complete test suite:
1. ✅ Automated code scan (no red flags)
2. ✅ 24-hour stress test (GPS signal loss recovery)
3. ✅ Network disconnect/reconnect handling
4. ✅ Malformed packet injection (NTP fuzzing)
5. ✅ Stack usage profiling in debugger
6. ✅ All three timing sources validated independently

## Resources

- **scripts/audit_embedded_c.py** - Automated vulnerability scanner
- **references/race-conditions.md** - ISR safety patterns and examples
- **references/stack-overflow.md** - Detection methods and mitigation
- **references/timing-validation.md** - GPS/NTP synchronization rules
- **references/network-security.md** - Packet validation and flood protection
- **references/common-bugs.md** - Field-tested bug patterns from production
