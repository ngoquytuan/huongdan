/**
 * @file IMMEDIATE_FIX_stable_frac_offset.md
 * @brief Immediate solutions for stack overflow in gps_once() → stable_frac_offset()
 * @date 2026-01-21
 */

# 🚨 GIẢI PHÁP NGAY LẬP TỨC - Stack Overflow Bug

## ❌ VẤN ĐỀ

```c
// Call chain TOO DEEP:
main()
  → system_main_loop()          // +32 bytes stack
    → slaveClockRun()           // +32 bytes
      → oneSecondfucns()        // +32 bytes
        → gps_once()            // +32 bytes
          → stable_frac_offset() // +32 bytes
            → LOG_DEBUG()       // +256 bytes (vsnprintf buffer)
            
// TOTAL: ~420 bytes chỉ từ call overhead!
// Khi gọi từ main loop (shallower) → OK
// Khi gọi từ gps_once (deeper) → STACK OVERFLOW!
```

---

## ✅ GIẢI PHÁP #1: INLINE LOGIC (KHUYẾN NGHỊ)

### File: gps.c hoặc slaveControl.c

```c
/**
 * @brief Handle GPS PPS synchronization check
 * @note INLINE version to reduce call depth
 */
void oneSecondfucns(void)
{
    // ... existing code ...
    
    // ✅ INLINE stable_frac_offset() logic HERE instead of calling gps_once()
    if(gps_every_sec == 1)
    {
        // Check work mode
        if(slave_clock.work_mode == GPS_MODE)
        {
            // Inline stable_frac_offset() logic
            DELTA_PPS_GPS_RTC = check_PPS_GPS;
            
            if(abs(DELTA_PPS_GPS_RTC) < 400) // 40ms
            {
                if(stable_delta_pulse < 10) stable_delta_pulse++;
                unstable_delta_pulse = 0;
            }
            else 
            {
                stable_delta_pulse = 0;
                if(unstable_delta_pulse < 10) unstable_delta_pulse++;
            }
        }
        
        // Simplified logging (reduced format string)
        LOG_DEBUG("gps", "%d:%d:%d sat:%d", 
                  GPS_hour, GPS_minute, GPS_second, gps_data.satellite_count);
        
        gps_every_sec = 0;
    }
    
    // ... rest of existing code ...
}

// ❌ REMOVE or COMMENT OUT gps_once() completely
// void gps_once(void) { ... }
```

**Lợi ích:**
- ✅ Giảm call depth từ 7 → 5 levels
- ✅ Tiết kiệm ~64 bytes stack (2 function calls)
- ✅ Code vẫn dễ đọc, dễ maintain

---

## ✅ GIẢI PHÁP #2: GỌI Ở MAIN LOOP (TỐT)

### File: system_init.c hoặc main.c

```c
void system_main_loop(void)
{
    slaveClockRun();  // Existing call
    
    // ✅ Handle GPS logic at SHALLOW level instead of deep call
    if(gps_every_sec == 1)
    {
        // Check work mode
        if(slave_clock.work_mode == GPS_MODE)
        {
            DELTA_PPS_GPS_RTC = check_PPS_GPS;
            
            if(abs(DELTA_PPS_GPS_RTC) < 400)
            {
                if(stable_delta_pulse < 10) stable_delta_pulse++;
                unstable_delta_pulse = 0;
            }
            else 
            {
                stable_delta_pulse = 0;
                if(unstable_delta_pulse < 10) unstable_delta_pulse++;
            }
            
            // Simple log at shallow depth
            LOG_DEBUG("gps", "PPS OK");
        }
        
        gps_every_sec = 0;
    }
}
```

**Lợi ích:**
- ✅ Giảm call depth từ 7 → 3 levels
- ✅ Tiết kiệm ~128 bytes stack
- ✅ Tách biệt GPS logic khỏi oneSecondfucns()

---

## ✅ GIẢI PHÁP #3: GIẢM LOG_DEBUG (NHANH)

### File: gps.c

```c
void gps_once(void)
{
    if(gps_every_sec == 1)
    {
        stable_frac_offset();
        
        // ❌ TRƯỚC - Quá nhiều arguments, format string dài
        // LOG_DEBUG("gps_once", "%d:%d:%d, %d-%d-%d, %d %c, offset %d ms, again %d",
        //           GPS_hour, GPS_minute, GPS_second, GPS_day, GPS_month, GPS_year,
        //           gps_data.satellite_count, gps_data.valid, 
        //           avg_gps_offset_stable/10, time_to_check_GPS_again);
        
        // ✅ SAU - Tách thành nhiều LOG ngắn HOẶC đơn giản hóa
        #ifdef DEBUG_GPS_VERBOSE
            LOG_DEBUG("gps", "Time: %02d:%02d:%02d", GPS_hour, GPS_minute, GPS_second);
            LOG_DEBUG("gps", "Sats: %d, Valid: %c", gps_data.satellite_count, gps_data.valid);
        #else
            // Production: minimal logging
            LOG_DEBUG("gps", "%02d:%02d sat:%d", GPS_hour, GPS_minute, gps_data.satellite_count);
        #endif
        
        gps_every_sec = 0;
    }
}
```

**Lợi ích:**
- ✅ Giảm vsnprintf buffer từ 256 → ~128 bytes
- ✅ Giữ nguyên call structure
- ✅ Dễ implement nhất

---

## ✅ GIẢI PHÁP #4: STATIC BUFFER (ADVANCED)

### File: debug_log.h

```c
// Thay vì dùng local buffer trong printf(), dùng global buffer
static char g_log_format_buffer[128];  // Smaller than default 256

#define LOG_DEBUG(tag, fmt, ...) \
    do { \
        if (current_log_level >= LOG_LEVEL_DEBUG) { \
            snprintf(g_log_format_buffer, sizeof(g_log_format_buffer), \
                     "[DEBUG][%s] " fmt "\r\n", tag, ##__VA_ARGS__); \
            log_output(g_log_format_buffer); \
        } \
    } while(0)
```

**Lợi ích:**
- ✅ Global buffer không chiếm stack
- ✅ Giảm stack usage trong mọi LOG_DEBUG call
- ⚠️ Cần cẩn thận với thread safety (không áp dụng nếu có RTOS)

---

## 🔧 GIẢI PHÁP BỔ SUNG: KHAI BÁO BIẾN

### Đừng quên khai báo volatile!

```c
// File: gps.c hoặc slaveControl.c

// ✅ CRITICAL: Phải khai báo volatile vì có thể được access từ interrupt
volatile int32_t DELTA_PPS_GPS_RTC = 0;
volatile uint8_t stable_delta_pulse = 0;
volatile uint8_t unstable_delta_pulse = 0;
```

**Nếu đã khai báo ở file khác, phải extern:**

```c
// File: gps.h hoặc slave_main.h
extern volatile int32_t DELTA_PPS_GPS_RTC;
extern volatile uint8_t stable_delta_pulse;
extern volatile uint8_t unstable_delta_pulse;
```

---

## 🎯 IMPLEMENTATION ROADMAP

### Bước 1: Immediate (5 phút)
```c
// Comment out gps_once() call
void oneSecondfucns(void) {
    // gps_once();  // ❌ Comment out
    gps_every_sec = 0;  // Reset flag manually
}
```
→ Test xem webpage còn bị mất không

### Bước 2: Quick Fix (10 phút)
Chọn 1 trong 3 giải pháp:
- Giải pháp #1: Inline logic vào oneSecondfucns()
- Giải pháp #2: Gọi ở system_main_loop()
- Giải pháp #3: Giảm LOG_DEBUG

### Bước 3: Add Monitoring (15 phút)
```c
#include "stack_monitor.h"

int main(void) {
    HAL_Init();
    Stack_Monitor_Init();  // ← Add this
    
    // ... init ...
    
    while(1) {
        system_main_loop();
        Stack_Monitor_Periodic();  // ← Add this
    }
}

void stable_frac_offset(void) {
    STACK_CHECK();  // ← Add this
    // ... code ...
}
```

### Bước 4: Verify (Testing)
1. Build và flash
2. Monitor log:
   ```
   [Stack] Monitor initialized
   [Stack] Size: 2048 bytes
   [DEBUG][gps] 12:34:56 sat:8
   ```
3. Kiểm tra webpage vẫn hoạt động
4. Để chạy 1 giờ, xem có crash không

---

## 📊 SO SÁNH GIẢI PHÁP

| Giải pháp | Độ khó | Hiệu quả | Stack tiết kiệm | Khuyến nghị |
|-----------|--------|----------|-----------------|-------------|
| #1 Inline | Dễ | Cao | ~64 bytes | ⭐⭐⭐⭐⭐ |
| #2 Main loop | Trung bình | Rất cao | ~128 bytes | ⭐⭐⭐⭐ |
| #3 Giảm LOG | Rất dễ | Trung bình | ~128 bytes | ⭐⭐⭐ |
| #4 Static buffer | Khó | Cao | ~256 bytes | ⭐⭐ |

**Khuyến nghị: Kết hợp #1 + #3**
- Inline logic vào oneSecondfucns()
- Giảm LOG_DEBUG format string
- Total tiết kiệm: ~192 bytes → Đủ để fix bug!

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. Tại sao webpage "mất"?

```
Stack overflow → Ghi đè vào global variables
              → webpage_content pointer bị corrupt
              → HTTP server trả về garbage data
              → Browser không hiển thị được webpage
```

**Không phải webpage trong Flash bị xóa!** Chỉ là con trỏ/data tạm thời bị corrupt.

### 2. Tại sao chỉ webpage bị ảnh hưởng?

Webpage data:
- Lớn (~20KB string constants)
- Con trỏ trỏ đến Flash
- HTTP server xử lý nhiều buffers

Khi stack overflow:
- Ghi đè vào vùng nhớ gần stack
- HTTP server buffers bị corrupt
- Webpage rendering fail

Clock/GPS vẫn chạy vì:
- Logic đơn giản
- Không dùng nhiều buffers
- Ít bị ảnh hưởng bởi stack corruption

### 3. Tại sao "có lúc có, lúc không"?

Stack overflow phụ thuộc:
- Timing: Khi nào hàm được gọi
- Interrupt timing: ISR có fire không
- Compiler optimization: -O0 vs -O2
- Temperature: Ảnh hưởng timing

→ **Không ổn định** là đặc trưng của stack overflow!

---

## 🆘 NẾU VẪN GẶP VẤN ĐỀ

Sau khi implement giải pháp trên, nếu vẫn có bug:

1. **Tăng stack size trong linker script:**
   ```ld
   _Min_Stack_Size = 0x1000; /* 4096 bytes */
   ```

2. **Kiểm tra các hàm khác:**
   ```bash
   grep -rn "char.*\[" *.c | grep -v static | grep -v "char \*"
   # Tìm tất cả local array declarations
   ```

3. **Build map file và analyze:**
   ```bash
   arm-none-eabi-gcc -Wl,-Map=output.map ...
   # Check stack usage trong map file
   ```

4. **Gửi log để analyze:**
   ```
   [Stack] SP in oneSecondfucns = 0x20003ABC
   [Stack] SP in gps_once = 0x20003900
   [Stack] SP in stable_frac_offset = 0x200037xx ← TOO LOW!
   ```

---

**LƯU Ý CUỐI:**
- ✅ Implement Giải pháp #1 (Inline) NGAY
- ✅ Thêm stack monitoring
- ✅ Test kỹ trước khi deploy
- ✅ Document changes trong code comments

Good luck! 🚀
