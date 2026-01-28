# GPS/NTP Timing Validation Rules

## Timing System Architecture

```
GPS (LEA-M8F)          NTP Server          DS3231 RTC
    |                      |                     |
    +-- NMEA (UART) -------+-- UDP packets ------+-- I2C
    +-- PPS (GPIO) --------+                     |
            |                                    |
            v                                    v
     [Time Source Selection Logic]              |
                    |                            |
                    v                            |
            [RTC Update Controller] -------------+
                    |
                    v
            [Display/SNMP Output]
```

## Critical Timing Offsets

### GPS PPS Edge-Triggered Timing

**The +1 Second Rule:**

```c
// ❌ WRONG - Missing offset
void PPS_IRQHandler(void) {
    DS3231_SetTime(gps_hour, gps_minute, gps_second);  
}
```

**Why wrong:** GPS sends NMEA sentence **BEFORE** the PPS pulse:
```
Timeline:
T+0.000s: NMEA sentence arrives "$GNRMC,123456.00,..." (time = 12:34:56)
T+0.100s: UART parsing completes, gps_second = 56
T+1.000s: PPS rising edge triggers interrupt
          ⚠️ But gps_second still = 56 (not 57!)
```

**✅ CORRECT:**
```c
void PPS_IRQHandler(void) {
    // PPS edge means "start of NEXT second"
    uint8_t next_second = gps_second + 1;
    
    if (next_second >= 60) {
        next_second = 0;
        // Handle minute/hour rollover
        increment_minute();
    }
    
    DS3231_SetTime(gps_hour, gps_minute, next_second);
}
```

### NTP Level-Based Timing

**No offset needed:**

```c
// ✅ CORRECT - NTP timestamp is already correct
void process_ntp_response(void) {
    uint32_t ntp_timestamp = extract_transmit_timestamp();
    
    // Convert NTP timestamp to UTC
    struct tm utc_time;
    ntp_to_utc(ntp_timestamp, &utc_time);
    
    // No +1 offset needed for NTP
    DS3231_SetTime(utc_time.hour, utc_time.minute, utc_time.second);
}
```

**Why different:** NTP timestamps represent **current time** at packet transmission, not future time like GPS PPS.

## Timing Validation Rules

### Rule 1: Satellite Count Threshold

```c
#define MIN_SATELLITES_FOR_SYNC 4  // Minimum for 3D fix

typedef struct {
    uint8_t satellite_count;
    uint8_t hdop;  // Horizontal Dilution of Precision
    char fix_quality;
    char valid;    // 'A' = valid, 'V' = invalid
} GPSStatus;

// ✅ CORRECT validation
bool gps_ready_for_sync(GPSStatus *status) {
    // Must have all conditions
    if (status->valid != 'A') return false;
    if (status->satellite_count < MIN_SATELLITES_FOR_SYNC) return false;
    if (status->hdop > 200) return false;  // HDOP > 2.0 is poor
    if (status->fix_quality < '1') return false;  // '0' = no fix
    
    return true;
}
```

**Bug pattern discovered:**
```c
// ❌ WRONG - Inconsistent state
if (gps_data.valid == 'A' && gps_data.satellite_count == 0) {
    // This should NEVER happen, but it does!
    // Root cause: Race condition between NMEA parsing
}
```

**Fix:** Atomic snapshot before validation:
```c
GPSStatus snapshot;
__disable_irq();
snapshot = gps_data;
__enable_irq();

if (gps_ready_for_sync(&snapshot)) {
    update_rtc();
}
```

### Rule 2: PPS Jitter Detection

```c
#define MAX_PPS_JITTER_US 1000  // 1ms tolerance

uint32_t last_pps_time = 0;
uint32_t pps_jitter_errors = 0;

void PPS_IRQHandler(void) {
    uint32_t current_time = TIM1->CNT;  // fractionOfSecond (0-9999)
    
    // PPS should arrive near beginning of second
    if (current_time > MAX_PPS_JITTER_US / 100) {  // Convert µs to 0.1ms
        pps_jitter_errors++;
        
        if (pps_jitter_errors > 3) {
            // PPS is unstable, don't trust GPS timing
            gps_timing_valid = 0;
        }
    } else {
        pps_jitter_errors = 0;  // Reset on good PPS
    }
}
```

### Rule 3: Time Jump Detection

```c
#define MAX_TIME_JUMP_SECONDS 60  // 1 minute tolerance

bool validate_time_update(RTCTime *old_time, RTCTime *new_time) {
    // Calculate time difference
    int32_t old_total = old_time->hour * 3600 + 
                        old_time->minute * 60 + 
                        old_time->second;
    
    int32_t new_total = new_time->hour * 3600 + 
                        new_time->minute * 60 + 
                        new_time->second;
    
    int32_t diff = new_total - old_total;
    
    // Handle midnight rollover
    if (diff < -43200) diff += 86400;  // -12h wraps to +12h
    if (diff > 43200) diff -= 86400;   // +12h wraps to -12h
    
    // Check if jump is too large
    if (abs(diff) > MAX_TIME_JUMP_SECONDS) {
        DEBUG_LOG("[ERROR] Time jump too large: %ld seconds", diff);
        return false;
    }
    
    return true;
}
```

### Rule 4: Source Stability Checking

```c
typedef enum {
    TIME_SOURCE_NONE,
    TIME_SOURCE_GPS,
    TIME_SOURCE_NTP,
    TIME_SOURCE_RTC
} TimeSource;

typedef struct {
    TimeSource current_source;
    uint32_t stable_count;       // Consecutive good updates
    uint32_t error_count;        // Consecutive errors
    uint32_t last_update_time;   // Systick timestamp
} TimeSourceState;

#define STABILITY_THRESHOLD 10   // 10 consecutive good updates
#define ERROR_THRESHOLD 5        // 5 consecutive errors before switch

TimeSourceState source_state;

void update_time_source(TimeSource source, bool success) {
    if (source != source_state.current_source) {
        // Source changed, reset counters
        source_state.stable_count = 0;
        source_state.error_count = 0;
    }
    
    if (success) {
        source_state.stable_count++;
        source_state.error_count = 0;
        source_state.last_update_time = HAL_GetTick();
        
        // Only trust source after stability threshold
        if (source_state.stable_count >= STABILITY_THRESHOLD) {
            source_state.current_source = source;
        }
    } else {
        source_state.error_count++;
        source_state.stable_count = 0;
        
        // Switch to backup source after error threshold
        if (source_state.error_count >= ERROR_THRESHOLD) {
            switch_to_backup_source();
        }
    }
}
```

## Fractional Second Synchronization

### Understanding fractionOfSecond (TIM1->CNT)

```c
// TIM1 configured to count 0-9999 per second
// Resolution: 0.1 millisecond (100 microseconds)

// Example readings:
TIM1->CNT = 0     → 0.000 seconds
TIM1->CNT = 1234  → 0.1234 seconds (123.4 ms)
TIM1->CNT = 5000  → 0.5000 seconds (500 ms)
TIM1->CNT = 9999  → 0.9999 seconds (999.9 ms)
```

### PPS Synchronization with Fractional Seconds

```c
void PPS_IRQHandler(void) {
    // ✅ Read counter at exact PPS edge
    volatile uint32_t fraction = TIM1->CNT;
    
    // Calculate jitter from expected zero
    if (fraction < 100 || fraction > 9900) {
        // Within 10ms of expected edge - good
        pps_sync_quality = GOOD;
    } else {
        // PPS arrived mid-second - GPS antenna issue?
        pps_sync_quality = POOR;
        DEBUG_LOG("[GPS] PPS jitter: fraction=%lu", fraction);
    }
    
    // Reset fractional counter to zero at PPS edge
    TIM1->CNT = 0;
}
```

### NTP Fractional Seconds

```c
// NTP timestamp format:
// 32 bits: Seconds since 1900-01-01
// 32 bits: Fraction of second (2^32 = 4,294,967,296)

void convert_ntp_fraction_to_mcu(uint32_t ntp_fraction) {
    // Convert NTP fraction (0 to 2^32-1) to MCU fraction (0 to 9999)
    uint32_t mcu_fraction = (uint64_t)ntp_fraction * 10000 / 4294967296ULL;
    
    // Set TIM1->CNT to sync fractional seconds
    TIM1->CNT = mcu_fraction;
}
```

## NMEA Sentence Timing

### Parse Timing Validation

```c
typedef struct {
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
    uint16_t millisecond;  // From fractional seconds in NMEA
    uint32_t arrival_tick;  // Systick when sentence arrived
} NMEATimestamp;

// ✅ CORRECT: Track both GPS time and local arrival time
void parse_gprmc(char *sentence) {
    NMEATimestamp ts;
    
    // Extract time fields
    sscanf(sentence, "$GNRMC,%2d%2d%2d.%3d", 
           &ts.hour, &ts.minute, &ts.second, &ts.millisecond);
    
    // Record local arrival time
    ts.arrival_tick = HAL_GetTick();
    
    // Validate: NMEA should arrive within 100ms of previous second
    uint32_t expected_tick = last_nmea_tick + 1000;  // +1 second
    int32_t delta = ts.arrival_tick - expected_tick;
    
    if (abs(delta) > 100) {
        DEBUG_LOG("[GPS] NMEA timing anomaly: %ld ms", delta);
        gps_timing_valid = 0;
    }
    
    last_nmea_tick = ts.arrival_tick;
}
```

## Time Source Priority Logic

```c
typedef enum {
    PRIORITY_GPS_LOCKED,      // GPS with good signal (highest)
    PRIORITY_NTP_STABLE,      // NTP with <10ms jitter
    PRIORITY_GPS_UNLOCKED,    // GPS with poor signal
    PRIORITY_NTP_UNSTABLE,    // NTP with >50ms jitter
    PRIORITY_RTC_ONLY         // No external sync (lowest)
} TimePriority;

TimePriority evaluate_time_source(void) {
    // GPS available and locked?
    if (gps_available && 
        gps_data.satellite_count >= 4 && 
        pps_jitter < 1000) {
        return PRIORITY_GPS_LOCKED;
    }
    
    // NTP available and stable?
    if (ntp_available && 
        ntp_jitter_ms < 10 && 
        ntp_stratum <= 3) {
        return PRIORITY_NTP_STABLE;
    }
    
    // GPS available but poor?
    if (gps_available && gps_data.valid == 'A') {
        return PRIORITY_GPS_UNLOCKED;
    }
    
    // NTP available but jittery?
    if (ntp_available) {
        return PRIORITY_NTP_UNSTABLE;
    }
    
    // No external source
    return PRIORITY_RTC_ONLY;
}

void select_time_source(void) {
    TimePriority current = evaluate_time_source();
    static TimePriority last = PRIORITY_RTC_ONLY;
    
    // Hysteresis: Only switch if new source is better
    if (current > last) {
        // Upgrading to better source
        last = current;
        apply_time_source(current);
    } else if (current < last - 1) {
        // Degraded by 2+ levels, switch immediately
        last = current;
        apply_time_source(current);
    }
    // Else: Stay with current source (avoid thrashing)
}
```

## Testing Procedures

### Test 1: GPS Signal Loss Recovery

```c
// Simulation:
1. Start with GPS locked (8 satellites)
2. Disconnect GPS antenna
3. Verify: System switches to NTP within 5 seconds
4. Verify: Clock continues with <10ms error
5. Reconnect GPS antenna
6. Verify: System re-locks within 30 seconds
7. Verify: Time jump < 1 second during transition
```

### Test 2: NTP Packet Loss

```c
// Simulation:
1. Start with NTP sync active
2. Block NTP port 123 on firewall
3. Verify: System detects timeout within 10 seconds
4. Verify: Switches to RTC-only mode gracefully
5. Unblock NTP port
6. Verify: System resumes NTP sync within 60 seconds
```

### Test 3: PPS Jitter Under Poor Weather

```c
// Simulation:
1. Monitor PPS interrupt timing
2. Induce interference (microwave, metal shield)
3. Log: fraction values at PPS edges
4. Verify: System detects jitter > 10ms
5. Verify: Marks GPS as unstable after 3 bad samples
6. Verify: Switches to NTP if available
```

### Test 4: Timezone Transition

```c
// Simulation:
1. Set timezone to UTC+5:30 (fractional offset)
2. Verify display shows correct local time
3. Change timezone to UTC-8:00
4. Verify display updates within 1 second
5. Check fractionOfSecond is not corrupted
```

## Common Pitfalls

### Pitfall 1: Ignoring NMEA Checksum

```c
// ❌ WRONG
void parse_gprmc(char *sentence) {
    sscanf(sentence, "$GNRMC,%2d%2d%2d", &h, &m, &s);
    // No checksum validation!
}

// ✅ CORRECT
bool verify_nmea_checksum(char *sentence) {
    char *star = strchr(sentence, '*');
    if (!star) return false;
    
    uint8_t checksum = 0;
    for (char *p = sentence + 1; p < star; p++) {
        checksum ^= *p;
    }
    
    uint8_t expected = strtol(star + 1, NULL, 16);
    return (checksum == expected);
}
```

### Pitfall 2: Assuming GPS Data is Always Fresh

```c
// ❌ WRONG
if (gps_data.valid == 'A') {
    update_rtc();  // May be using stale data!
}

// ✅ CORRECT
#define GPS_DATA_TIMEOUT_MS 2000

if (gps_data.valid == 'A' && 
    (HAL_GetTick() - gps_data.last_update) < GPS_DATA_TIMEOUT_MS) {
    update_rtc();
}
```

### Pitfall 3: Not Handling Leap Seconds

```c
// GPS includes leap second information in NMEA
void handle_leap_second(void) {
    if (gps_data.leap_second_pending) {
        // UTC will insert 23:59:60 before midnight
        DEBUG_LOG("[GPS] Leap second pending");
        
        // Prepare RTC for 61-second minute
        rtc_leap_second_mode = 1;
    }
}
```

## Summary Checklist

Before deploying timing system:

- [ ] GPS PPS adds +1 second offset
- [ ] NTP timestamps use no offset  
- [ ] Satellite count >= 4 before GPS sync
- [ ] PPS jitter monitored (<1ms threshold)
- [ ] Time jumps validated (<60s threshold)
- [ ] Source stability requires 10 good samples
- [ ] Fractional seconds synchronized to 0.1ms
- [ ] NMEA checksums validated
- [ ] GPS data timeout checked (<2s stale)
- [ ] Source switching uses hysteresis
- [ ] Tested: GPS signal loss recovery
- [ ] Tested: NTP packet loss handling
- [ ] Tested: PPS jitter detection
- [ ] Tested: Timezone fractional offsets
