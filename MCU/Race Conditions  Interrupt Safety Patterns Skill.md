# Race Conditions & Interrupt Safety Patterns

## The Fundamental Problem

Race conditions occur when:
1. **Multiple execution contexts** (ISR + main loop) access shared data
2. **No synchronization** mechanism protects the access
3. **Timing-dependent** outcomes cause non-deterministic bugs

## Critical Detection Patterns

### Pattern 1: Exact Comparisons with Interrupt Counters

**🔴 DANGER ZONE:**
```c
volatile uint32_t pps_counter = 0;

void PPS_IRQHandler(void) {
    pps_counter++;  // Increments at unpredictable times
}

void main(void) {
    while(1) {
        // ❌ WRONG: May miss the exact moment
        if (pps_counter == 1000) {
            do_sync();
        }
    }
}
```

**Why it fails:** If main loop is busy when `pps_counter` changes from 999 to 1000, it misses the comparison and never triggers.

**✅ CORRECT FIX:**
```c
void main(void) {
    static uint32_t last_processed = 0;
    
    while(1) {
        uint32_t current = pps_counter;  // Atomic read
        
        // Range comparison catches missed updates
        if (current >= last_processed + 1000) {
            do_sync();
            last_processed = current;
        }
    }
}
```

### Pattern 2: Missing Volatile Keywords

**🔴 DANGER ZONE:**
```c
uint32_t gps_time_updated = 0;  // ❌ Missing volatile!

void UART_IRQHandler(void) {
    // Parse GPS data
    gps_time_updated = 1;  // Compiler may optimize this away
}

void main(void) {
    while(1) {
        // ❌ Compiler may cache this value in register
        if (gps_time_updated) {
            process_gps_time();
            gps_time_updated = 0;
        }
    }
}
```

**Why it fails:** Compiler assumes `gps_time_updated` doesn't change during main loop execution, caches it in a register, and never sees the ISR update.

**✅ CORRECT FIX:**
```c
volatile uint32_t gps_time_updated = 0;  // ✅ Forces memory read every time
```

### Pattern 3: Multi-Byte Data Corruption

**🔴 DANGER ZONE:**
```c
typedef struct {
    uint32_t timestamp;    // 4 bytes
    uint16_t fraction;     // 2 bytes
    uint8_t valid;         // 1 byte
} GPSTime;

GPSTime gps_data;  // ❌ Missing volatile, no atomic access

void GPS_IRQHandler(void) {
    gps_data.timestamp = new_timestamp;
    gps_data.fraction = new_fraction;
    gps_data.valid = 'A';
}

void main(void) {
    // ❌ WRONG: Reading while ISR may be writing
    if (gps_data.valid == 'A') {
        uint32_t time = gps_data.timestamp;  // May be partially updated!
    }
}
```

**Why it fails:** ARM Cortex-M can be interrupted mid-struct-copy. Main reads `timestamp` while ISR is halfway through writing it.

**✅ CORRECT FIX - Atomic Snapshot:**
```c
typedef struct {
    uint32_t timestamp;
    uint16_t fraction;
    uint8_t valid;
} GPSTime;

volatile GPSTime gps_data;  // ✅ Volatile

void main(void) {
    GPSTime snapshot;
    
    // ✅ Atomic copy with interrupts disabled
    __disable_irq();
    snapshot = gps_data;
    __enable_irq();
    
    // Now safe to use snapshot
    if (snapshot.valid == 'A') {
        process_time(snapshot.timestamp);
    }
}
```

**Alternative: Double-Buffering**
```c
typedef struct {
    uint32_t timestamp;
    uint16_t fraction;
    uint8_t valid;
} GPSTime;

volatile GPSTime gps_buffer[2];  // ✅ Ping-pong buffers
volatile uint8_t write_index = 0;

void GPS_IRQHandler(void) {
    uint8_t idx = write_index;
    gps_buffer[idx].timestamp = new_timestamp;
    gps_buffer[idx].fraction = new_fraction;
    gps_buffer[idx].valid = 'A';
    
    write_index = 1 - idx;  // Swap buffers atomically
}

void main(void) {
    uint8_t read_index = 1 - write_index;  // Read from opposite buffer
    GPSTime snapshot = gps_buffer[read_index];  // Safe, ISR not writing here
}
```

## Blocking Operations in Critical Paths

### Pattern 4: I2C/SPI in Interrupt Context

**🔴 DANGER ZONE:**
```c
void PPS_IRQHandler(void) {
    EXTI->PR = EXTI_PR_PR9;
    
    // ❌ WRONG: Blocking I2C read (100-600ms!)
    DS3231_ReadTime(&rtc_time);
    
    // ❌ Other interrupts blocked for hundreds of milliseconds
    update_display();
}
```

**Why it fails:** 
- I2C clock stretching can block for 100-600ms
- Other interrupts (like GPS UART) get delayed or missed
- Violates sub-millisecond timing requirements

**✅ CORRECT FIX - Deferred Processing:**
```c
volatile uint8_t pps_flag = 0;

void PPS_IRQHandler(void) {
    EXTI->PR = EXTI_PR_PR9;
    
    // ✅ Only set flag, no blocking operations
    pps_flag = 1;
}

void main(void) {
    while(1) {
        if (pps_flag) {
            pps_flag = 0;
            
            // ✅ Safe to block in main loop
            DS3231_ReadTime(&rtc_time);
            update_display();
        }
    }
}
```

### Pattern 5: Printf/Debug in ISR

**🔴 DANGER ZONE:**
```c
void UART_IRQHandler(void) {
    char byte = UART->DR;
    
    // ❌ WRONG: printf is NOT reentrant!
    printf("Received: %c\n", byte);
    
    // ❌ May corrupt heap if main loop also uses printf
}
```

**✅ CORRECT FIX - Buffered Logging:**
```c
#define LOG_BUFFER_SIZE 256
volatile char log_buffer[LOG_BUFFER_SIZE];
volatile uint16_t log_index = 0;

void UART_IRQHandler(void) {
    char byte = UART->DR;
    
    // ✅ Fast buffer write
    if (log_index < LOG_BUFFER_SIZE - 1) {
        log_buffer[log_index++] = byte;
    }
}

void main(void) {
    while(1) {
        if (log_index > 0) {
            __disable_irq();
            uint16_t len = log_index;
            log_index = 0;
            __enable_irq();
            
            // ✅ Safe printf in main context
            for (uint16_t i = 0; i < len; i++) {
                printf("%c", log_buffer[i]);
            }
        }
    }
}
```

## Real-World Bug Examples

### Bug 1: GPS Time Corruption During PPS

**Symptom:** Clock occasionally jumps by random hours/minutes

**Root cause:**
```c
// ❌ WRONG
struct {
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
} gps_time;  // Missing volatile

void UART_IRQHandler(void) {
    gps_time.hour = parsed_hour;    // Write byte 0
    gps_time.minute = parsed_minute; // Write byte 1
    gps_time.second = parsed_second; // Write byte 2
}

void PPS_IRQHandler(void) {
    // ❌ Reading mid-update!
    update_rtc(gps_time.hour, gps_time.minute, gps_time.second);
}
```

**Fix:** Atomic snapshot with interrupts disabled

### Bug 2: NTP Packet Race with UDP RX

**Symptom:** NTP client randomly hangs, never receives response

**Root cause:**
```c
void process_ntp_response(void) {
    uint16_t len = W5500_GetRxSize();  // Returns 48
    
    // ❌ Race: New packet arrives here, doubles buffer!
    
    uint8_t buffer[len];  // Allocates 48 bytes
    W5500_ReadData(buffer, len);  // Tries to read 96 bytes -> overflow!
}
```

**Fix:** Quota-based reading, validate length

## Automated Detection Commands

```bash
# Find exact comparisons with volatile variables
grep -E "if.*==.*volatile|volatile.*==" *.c

# Find missing volatile on shared variables
grep -E "^[^/]*\s+(uint|int|char).*\s+\w+\s*;" *.c | grep -v volatile

# Find blocking calls in ISR handlers
grep -A 20 "IRQHandler" *.c | grep -E "HAL_I2C|HAL_SPI|printf|HAL_Delay"

# Find printf with many arguments (stack overflow risk)
grep -E "printf.*%.*%.*%.*%.*%" *.c
```

## Testing Procedures

### Test 1: Interrupt Stress Test
```c
// Rapidly toggle GPIO to trigger PPS interrupts
while(test_active) {
    HAL_GPIO_WritePin(PPS_PORT, PPS_PIN, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(PPS_PORT, PPS_PIN, GPIO_PIN_RESET);
    HAL_Delay(1);
}
// Check for data corruption, missed events
```

### Test 2: Long Duration Race Detection
```c
// Run for 24+ hours
// Log every ISR execution timestamp
// Analyze logs for gaps, timing anomalies
```

### Test 3: Concurrent Load Test
```c
// Simultaneously:
// - GPS sending NMEA sentences (1 Hz)
// - PPS interrupts (1 Hz)
// - NTP packets (10 Hz)
// - Display updates (10 Hz)
// - Web server requests (variable)
// Monitor for deadlocks, corruption
```

## Summary Checklist

Before releasing embedded code, verify:

- [ ] All ISR-modified variables are `volatile`
- [ ] No exact `==` comparisons with interrupt counters
- [ ] Multi-byte structs use atomic snapshots
- [ ] No blocking I2C/SPI/UART in ISRs
- [ ] No printf/malloc/free in ISRs
- [ ] Critical sections use `__disable_irq()` / `__enable_irq()`
- [ ] Double-buffering or flags for deferred processing
- [ ] Stress tested with concurrent interrupt sources
- [ ] Stack usage profiled under maximum interrupt nesting
