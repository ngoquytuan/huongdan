# Common Embedded Systems Bugs - Field-Tested Patterns

This document contains real bugs discovered in production embedded systems, with root causes and fixes.

## Category 1: Timing & Synchronization Bugs

### Bug #1: GPS Time Corruption During PPS

**Symptom:** Clock jumps to random time (e.g., 23:45 instead of 12:34)

**Code:**
```c
// Global GPS data (not volatile!)
struct {
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
    char valid;
} gps_time;

// UART interrupt parses NMEA
void UART3_IRQHandler(void) {
    char byte = USART3->RDR;
    // Parse NMEA sentence...
    gps_time.hour = parsed_hour;
    gps_time.minute = parsed_minute;
    gps_time.second = parsed_second;
    gps_time.valid = 'A';
}

// PPS interrupt reads GPS time
void EXTI9_5_IRQHandler(void) {
    // ❌ WRONG: Reading multi-byte struct mid-update!
    DS3231_SetTime(gps_time.hour, gps_time.minute, gps_time.second);
}
```

**Root Cause:** Race condition. PPS interrupt fires while UART interrupt is updating GPS time struct. Reads corrupted partial data.

**Timeline:**
```
T+0.000: UART starts parsing NMEA
T+0.050: UART writes hour=12
T+0.100: PPS interrupt fires HERE
         Reads: hour=12, minute=<old value>, second=<old value>
T+0.150: UART writes minute=34
T+0.200: UART writes second=56
```

**Fix:**
```c
volatile struct {
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
    char valid;
} gps_time;

void EXTI9_5_IRQHandler(void) {
    // ✅ Atomic snapshot
    struct {
        uint8_t hour;
        uint8_t minute;
        uint8_t second;
        char valid;
    } snapshot;
    
    __disable_irq();
    snapshot = gps_time;
    __enable_irq();
    
    if (snapshot.valid == 'A') {
        DS3231_SetTime(snapshot.hour, snapshot.minute, snapshot.second);
    }
}
```

---

### Bug #2: Exact Comparison with PPS Counter

**Symptom:** System occasionally fails to sync time, requires reboot

**Code:**
```c
volatile uint32_t pps_counter = 0;

void EXTI9_5_IRQHandler(void) {
    pps_counter++;
}

void main(void) {
    while(1) {
        // ❌ WRONG: Exact comparison
        if (pps_counter == 10) {
            synchronize_rtc();
        }
    }
}
```

**Root Cause:** Main loop busy processing when `pps_counter` transitions from 9→10. Misses exact moment, never syncs.

**Fix:**
```c
void main(void) {
    static uint32_t last_sync = 0;
    
    while(1) {
        // ✅ Range comparison
        if (pps_counter >= last_sync + 10) {
            synchronize_rtc();
            last_sync = pps_counter;
        }
    }
}
```

---

### Bug #3: Blocking I2C in PPS Interrupt

**Symptom:** GPS UART data corruption, missed PPS events, 100ms timing jitter

**Code:**
```c
void EXTI9_5_IRQHandler(void) {
    EXTI->PR = EXTI_PR_PR9;
    
    // ❌ WRONG: Blocking I2C read
    DS3231_ReadTime(&rtc_time);  // Takes 100-600ms!
    
    // Update display
    update_7segment_display();
}
```

**Root Cause:** I2C clock stretching blocks interrupt for hundreds of milliseconds. Other interrupts (GPS UART) get delayed/missed.

**Fix:**
```c
volatile uint8_t pps_flag = 0;

void EXTI9_5_IRQHandler(void) {
    EXTI->PR = EXTI_PR_PR9;
    pps_flag = 1;  // ✅ Set flag only
}

void main(void) {
    while(1) {
        if (pps_flag) {
            pps_flag = 0;
            DS3231_ReadTime(&rtc_time);  // ✅ Safe in main loop
            update_7segment_display();
        }
    }
}
```

---

## Category 2: Stack Overflow Bugs

### Bug #4: Large HTML Buffer on Stack

**Symptom:** Webpage loads fine initially, then suddenly stops working. LED display and NTP continue functioning.

**Code:**
```c
void httpServer_generate_config_page(void) {
    char html[1536];  // ❌ 1.5KB on stack!
    
    sprintf(html, "<html><head><title>Config</title>");
    strcat(html, "<body><h1>Clock Configuration</h1>");
    // ...50 more lines of HTML generation
    
    W5500_SendData(http_socket, html, strlen(html));
}
```

**Root Cause:** 
- Stack overflow corrupts global variables
- Specifically corrupts `http_connection_state` variable
- Webpage stops working, but other features (using different globals) continue

**Call stack depth:**
```
main() → http_process() → generate_config_page() → sprintf() → __vfprintf()
  32B      128B             1536B                    256B       384B
= 2336 bytes (exceeds 2KB stack!)
```

**Fix:**
```c
static char html_buffer[1536];  // ✅ Move to static storage

void httpServer_generate_config_page(void) {
    sprintf(html_buffer, "<html><head><title>Config</title>");
    // ...
    W5500_SendData(http_socket, html_buffer, strlen(html_buffer));
}
```

---

### Bug #5: Printf with 12+ Arguments

**Symptom:** Random hard faults, stack corruption

**Code:**
```c
void log_gps_status(void) {
    // ❌ WRONG: 12 arguments = ~96 bytes stack
    sprintf(buffer,
        "GPS: %d/%d/%d %d:%d:%d lat=%ld lon=%ld alt=%d sat=%d hdop=%d fix=%c",
        year, month, day, hour, minute, second,
        latitude, longitude, altitude, satellites, hdop, fix_quality);
}
```

**Root Cause:** Each argument pushed to stack. Format parsing allocates temporary buffers. Total stack usage ~300+ bytes for one call.

**Fix:**
```c
void log_gps_status(void) {
    // ✅ Split into smaller calls
    sprintf(buffer, "GPS: %d/%d/%d %d:%d:%d", 
        year, month, day, hour, minute, second);
    
    char temp[32];
    sprintf(temp, " lat=%ld lon=%ld", latitude, longitude);
    strcat(buffer, temp);
    
    sprintf(temp, " alt=%d sat=%d", altitude, satellites);
    strcat(buffer, temp);
}
```

---

## Category 3: Network Security Bugs

### Bug #6: NTP Buffer Deadlock

**Symptom:** NTP client sends request, never receives response, system hangs

**Code:**
```c
void process_ntp_response(void) {
    uint16_t len = W5500_GetRxSize();  // Returns 48
    
    // ❌ Race: New packet arrives here!
    //     RX buffer now has 96 bytes
    
    uint8_t buffer[48];
    W5500_ReadData(buffer, len);  // Tries to read 96 bytes → overflow!
}
```

**Root Cause:** Race between `GetRxSize()` and `ReadData()`. Second packet arrives, doubles buffer size, causes read overflow.

**Fix:**
```c
#define MAX_NTP_PACKET 48

void process_ntp_response(void) {
    uint16_t len = W5500_GetRxSize();
    
    // ✅ Cap to maximum expected size
    if (len > MAX_NTP_PACKET) {
        len = MAX_NTP_PACKET;
    }
    
    uint8_t buffer[MAX_NTP_PACKET];
    W5500_ReadData(buffer, len);
    
    // ✅ Validate packet
    if (len != 48) {
        DEBUG_LOG("[NTP] Invalid packet size: %d", len);
        return;
    }
}
```

---

### Bug #7: UDP Spoofing Time Injection

**Symptom:** Clock suddenly jumps to wrong time, no error logs

**Code:**
```c
void W5500_NTP_Handler(void) {
    uint8_t buffer[48];
    uint16_t len = W5500_RecvData(buffer, 48);
    
    // ❌ WRONG: No validation!
    process_ntp_packet(buffer);
}
```

**Root Cause:** Attacker sends spoofed NTP packet with fake timestamp. System blindly accepts it.

**Fix:**
```c
void W5500_NTP_Handler(void) {
    uint8_t src_ip[4];
    uint16_t src_port;
    uint8_t buffer[48];
    uint16_t len;
    
    W5500_GetRemoteInfo(&src_ip, &src_port);
    len = W5500_RecvData(buffer, 48);
    
    // ✅ Validate source
    if (!is_trusted_ntp_server(src_ip)) {
        DEBUG_LOG("[NTP] Rejected packet from %d.%d.%d.%d",
            src_ip[0], src_ip[1], src_ip[2], src_ip[3]);
        return;
    }
    
    // ✅ Validate packet format
    if (!validate_ntp_packet(buffer, len)) {
        DEBUG_LOG("[NTP] Invalid packet format");
        return;
    }
    
    // ✅ Validate timestamp range
    if (!validate_ntp_timestamp(buffer)) {
        DEBUG_LOG("[NTP] Timestamp out of range");
        return;
    }
    
    process_ntp_packet(buffer);
}
```

---

## Category 4: String Handling Bugs

### Bug #8: Missing Null Terminator

**Symptom:** Display shows garbage characters after GPS name

**Code:**
```c
void parse_gprmc(char *sentence) {
    char time_str[6];
    
    // ❌ WRONG: strncpy doesn't guarantee null terminator
    strncpy(time_str, sentence + 7, 6);
    
    sscanf(time_str, "%2d%2d%2d", &hour, &minute, &second);
}
```

**Root Cause:** `strncpy()` doesn't add null terminator if source is ≥ size. `sscanf()` reads past buffer.

**Fix:**
```c
void parse_gprmc(char *sentence) {
    char time_str[7];  // ✅ +1 for null terminator
    
    strncpy(time_str, sentence + 7, 6);
    time_str[6] = '\0';  // ✅ Force null terminator
    
    sscanf(time_str, "%2d%2d%2d", &hour, &minute, &second);
}
```

---

### Bug #9: Buffer Overflow in NMEA Parsing

**Symptom:** System crashes when GPS sends long sentence

**Code:**
```c
char gps_buffer[80];
uint8_t gps_index = 0;

void UART3_IRQHandler(void) {
    char byte = USART3->RDR;
    
    // ❌ WRONG: No bounds check!
    gps_buffer[gps_index++] = byte;
    
    if (byte == '\n') {
        parse_nmea(gps_buffer);
        gps_index = 0;
    }
}
```

**Root Cause:** Malformed NMEA sentence without '\n' causes `gps_index` to exceed buffer size.

**Fix:**
```c
void UART3_IRQHandler(void) {
    char byte = USART3->RDR;
    
    // ✅ Bounds check
    if (gps_index < sizeof(gps_buffer) - 1) {
        gps_buffer[gps_index++] = byte;
    } else {
        // Buffer overflow protection
        DEBUG_LOG("[GPS] Buffer overflow, resetting");
        gps_index = 0;
        return;
    }
    
    if (byte == '\n') {
        gps_buffer[gps_index] = '\0';  // ✅ Null terminate
        parse_nmea(gps_buffer);
        gps_index = 0;
    }
}
```

---

## Category 5: Hardware-Specific Bugs

### Bug #10: W5500 Socket Not Ready

**Symptom:** Network communication works initially, then stops

**Code:**
```c
void send_ntp_request(void) {
    uint8_t packet[48];
    prepare_ntp_packet(packet);
    
    // ❌ WRONG: No socket state check
    W5500_SendData(NTP_SOCKET, packet, 48);
}
```

**Root Cause:** Socket closed by remote host or timeout. W5500 in invalid state.

**Fix:**
```c
void send_ntp_request(void) {
    uint8_t status = W5500_GetSocketStatus(NTP_SOCKET);
    
    // ✅ Check socket state
    if (status != SOCK_UDP) {
        DEBUG_LOG("[W5500] Socket %d not ready (state=0x%02X)",
            NTP_SOCKET, status);
        
        // Recover by closing and reopening
        W5500_Close(NTP_SOCKET);
        W5500_Socket(NTP_SOCKET, Sn_MR_UDP, NTP_PORT, 0);
        return;
    }
    
    uint8_t packet[48];
    prepare_ntp_packet(packet);
    W5500_SendData(NTP_SOCKET, packet, 48);
}
```

---

### Bug #11: DS3231 I2C Hung

**Symptom:** System freezes intermittently, watchdog resets

**Code:**
```c
void DS3231_ReadTime(RTCTime *time) {
    // ❌ WRONG: No timeout or error handling
    HAL_I2C_Master_Receive(&hi2c1, DS3231_ADDR, buffer, 7, HAL_MAX_DELAY);
    
    time->second = bcd_to_bin(buffer[0]);
    time->minute = bcd_to_bin(buffer[1]);
    time->hour = bcd_to_bin(buffer[2]);
}
```

**Root Cause:** I2C bus hung (SDA stuck low). `HAL_MAX_DELAY` causes infinite wait, watchdog doesn't get refreshed.

**Fix:**
```c
#define I2C_TIMEOUT_MS 100
#define I2C_MAX_RETRIES 3

bool DS3231_ReadTime(RTCTime *time) {
    uint8_t buffer[7];
    uint8_t retries = 0;
    
    while (retries < I2C_MAX_RETRIES) {
        // ✅ Timeout specified
        HAL_StatusTypeDef status = HAL_I2C_Master_Receive(
            &hi2c1, DS3231_ADDR, buffer, 7, I2C_TIMEOUT_MS);
        
        if (status == HAL_OK) {
            time->second = bcd_to_bin(buffer[0]);
            time->minute = bcd_to_bin(buffer[1]);
            time->hour = bcd_to_bin(buffer[2]);
            return true;
        }
        
        DEBUG_LOG("[RTC] I2C error: %d (retry %d)", status, retries);
        
        // ✅ Attempt recovery
        HAL_I2C_DeInit(&hi2c1);
        HAL_Delay(10);
        HAL_I2C_Init(&hi2c1);
        
        retries++;
    }
    
    DEBUG_LOG("[RTC] I2C failed after %d retries", retries);
    return false;
}
```

---

## Category 6: Logic Errors

### Bug #12: GPS Valid='A' but Satellites=0

**Symptom:** System syncs time with invalid GPS data, clock drifts

**Code:**
```c
if (gps_data.valid == 'A') {
    // ❌ WRONG: Trusting 'valid' flag only
    update_rtc_from_gps();
}
```

**Root Cause:** GPS module sets `valid='A'` even when satellite count drops to zero due to weather. Firmware bug in LEA-M8F.

**Fix:**
```c
if (gps_data.valid == 'A' && 
    gps_data.satellite_count >= 4 &&
    gps_data.hdop < 200 &&
    gps_data.fix_quality >= '1') {
    // ✅ Multiple validation criteria
    update_rtc_from_gps();
} else {
    DEBUG_LOG("[GPS] Rejected: valid=%c sat=%d hdop=%d fix=%c",
        gps_data.valid, gps_data.satellite_count, 
        gps_data.hdop, gps_data.fix_quality);
}
```

---

### Bug #13: Timezone Fractional Offset Corruption

**Symptom:** Display shows wrong minute after timezone change (e.g., 30 minutes off)

**Code:**
```c
int8_t timezone_hours = 5;
int8_t timezone_minutes = 30;  // India: UTC+5:30

void apply_timezone(uint8_t utc_hour, uint8_t utc_minute) {
    // ❌ WRONG: Integer overflow
    uint8_t local_hour = utc_hour + timezone_hours;
    uint8_t local_minute = utc_minute + timezone_minutes;
    
    // If local_minute >= 60, overflow!
}
```

**Root Cause:** Didn't handle minute rollover when adding timezone offset.

**Fix:**
```c
void apply_timezone(uint8_t utc_hour, uint8_t utc_minute) {
    int16_t total_minutes = utc_hour * 60 + utc_minute;
    int16_t offset_minutes = timezone_hours * 60 + timezone_minutes;
    
    // ✅ Calculate total
    total_minutes += offset_minutes;
    
    // ✅ Handle day rollover
    if (total_minutes < 0) {
        total_minutes += 24 * 60;
    } else if (total_minutes >= 24 * 60) {
        total_minutes -= 24 * 60;
    }
    
    uint8_t local_hour = total_minutes / 60;
    uint8_t local_minute = total_minutes % 60;
}
```

---

## Pattern Summary

| Bug Type | Count | Detection Method |
|----------|-------|------------------|
| Race conditions | 3 | Code review, stress testing |
| Stack overflow | 2 | Stack watermarking, -fstack-usage |
| Network security | 2 | Packet fuzzing, penetration testing |
| String handling | 2 | Static analysis, buffer overflow detection |
| Hardware issues | 2 | Timeout testing, fault injection |
| Logic errors | 2 | Unit testing, long-duration validation |

## Prevention Techniques

1. **Always use volatile** for ISR-shared variables
2. **Range comparisons** (>=) instead of exact (==) with counters
3. **Atomic snapshots** with `__disable_irq()` for multi-byte data
4. **Static/global storage** for large buffers (>64 bytes)
5. **Packet validation** (length, format, source, timestamp)
6. **Null terminators** after every `strncpy()`
7. **Bounds checking** in all buffer operations
8. **Timeout handling** for all blocking operations
9. **Multi-criteria validation** (don't trust single flag)
10. **Integer overflow protection** in arithmetic

## Detection Tools

- Static analysis: `-fstack-usage`, Cppcheck, Clang-Tidy
- Runtime: Stack watermarking, UART debug logs
- Testing: Fuzzing, packet injection, stress tests
- Hardware: Logic analyzer, oscilloscope for PPS/I2C timing
