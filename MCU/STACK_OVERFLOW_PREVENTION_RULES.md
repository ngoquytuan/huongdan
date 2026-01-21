# 🛡️ QUY TẮC CODE PHÒNG TRÁNH STACK OVERFLOW - STM32 BARE METAL

## 📋 MỤC LỤC
1. [Hiểu về Stack Overflow](#1-hiểu-về-stack-overflow)
2. [15 Quy Tắc Vàng](#2-15-quy-tắc-vàng)
3. [Patterns Nguy Hiểm](#3-patterns-nguy-hiểm-phải-tránh)
4. [Stack Safety Checklist](#4-stack-safety-checklist)
5. [Tools và Debug](#5-tools-và-debug-methods)

---

## 1. HIỂU VỀ STACK OVERFLOW

### Triệu chứng điển hình:
- ✅ Code chạy OK từ main loop
- ❌ Code crash khi gọi từ hàm sâu hơn
- ❌ Webpage/Flash data bị "mất" hoặc corrupt
- ❌ Biến toàn cục bị thay đổi ngẫu nhiên
- ❌ Hard fault không rõ nguyên nhân

### Tại sao webpage bị mất?

```
Stack Memory Layout (STM32G474):
┌──────────────────┐ 0x20000000 (RAM start)
│   .data          │ ← Global variables
│   .bss           │ ← Zero-initialized vars
├──────────────────┤
│   Heap (grows ↓) │
├──────────────────┤
│   Free space     │
├──────────────────┤
│   Stack (grows ↓)│ ← SP (Stack Pointer)
│                  │
│   ❌ OVERFLOW!   │ ← Ghi đè vào heap/globals!
└──────────────────┘ 0x20018000 (RAM end)
```

**Khi stack overflow:**
- Stack pointer giảm xuống quá thấp
- Ghi đè vào vùng nhớ của biến toàn cục
- **Webpage pointers bị corrupt** → "webpage mất"
- Biến ngẫu nhiên thay đổi giá trị

---

## 2. 15 QUY TẮC VÀNG

### ⭐ QUY TẮC #1: GIỚI HẠN CALL DEPTH
**Mức độ:** 🔴 CRITICAL

```c
/* ❌ SẼ TRÀN STACK */
void level1(void) {
    char buf[100];
    level2();
}
void level2(void) {
    char buf[200];
    level3();
}
void level3(void) {
    char buf[300];
    level4();
}
// Total: 100+200+300 = 600 bytes chỉ từ local arrays!

/* ✅ AN TOÀN */
void level1(void) {
    static char shared_buf[300];  // Shared, không chiếm stack
    level2(shared_buf);
}
void level2(char *buf) {
    // Reuse buffer, không tạo mới
    level3(buf);
}
```

**Quy định:**
- ❌ Không gọi hàm sâu quá **5 cấp** khi có buffer lớn
- ✅ Ưu tiên buffer static/global cho hàm nested
- ✅ Mỗi cấp gọi hàm = ~32-64 bytes overhead (return address, registers)

---

### ⭐ QUY TẮC #2: TRÁNH LOCAL ARRAY LỚN
**Mức độ:** 🔴 CRITICAL

```c
/* ❌ NGUY HIỂM - 1024 bytes trên stack! */
void process_data(void) {
    char buffer[1024];      // ❌ Quá lớn!
    uint32_t temp[256];     // ❌ 1024 bytes nữa!
    // ... code ...
}

/* ✅ GIẢI PHÁP 1: Static buffer */
void process_data(void) {
    static char buffer[1024];  // Nằm trong .bss, không chiếm stack
    // ... code ...
}

/* ✅ GIẢI PHÁP 2: Global buffer */
static char g_work_buffer[1024];  // File scope

void process_data(void) {
    // Dùng g_work_buffer
}

/* ✅ GIẢI PHÁP 3: Dynamic allocation (cẩn thận!) */
void process_data(void) {
    char *buffer = malloc(1024);
    if(buffer == NULL) {
        LOG_ERROR("Mem", "Out of memory!");
        return;
    }
    // ... use buffer ...
    free(buffer);
}
```

**Quy định:**
- ❌ Local array > **128 bytes** là nguy hiểm
- ❌ Local array > **256 bytes** là RẤT nguy hiểm
- ✅ Dùng `static` cho buffer > 128 bytes
- ✅ Dùng global cho buffer shared giữa nhiều hàm

---

### ⭐ QUY TẮC #3: CẢNH GIÁC VỚI printf/LOG_DEBUG
**Mức độ:** 🟠 HIGH

```c
/* ❌ NGUY HIỂM */
void gps_once(void) {
    LOG_DEBUG("GPS", "Time: %d:%d:%d, offset: %d, satellites: %d, quality: %f",
              hour, min, sec, offset, sat_count, quality);
    // vsnprintf() internal buffer = 256-512 bytes!
}

/* ✅ AN TOÀN - Giới hạn format string */
void gps_once(void) {
    LOG_DEBUG("GPS", "Time: %02d:%02d:%02d", hour, min, sec);  // Ngắn gọn
    LOG_DEBUG("GPS", "Offset: %d ms", offset/10);              // Tách ra
}

/* ✅ TỐT NHẤT - Disable trong production */
#ifdef DEBUG_MODE
    LOG_DEBUG("GPS", "Detailed info: ...");
#endif
```

**Quy định:**
- ❌ Không dùng `printf()` với quá 5 arguments
- ❌ Format string không dài quá 80 ký tự
- ✅ Tách thành nhiều LOG_DEBUG nhỏ
- ✅ Disable debug logging trong production build

**Hiểu rõ vấn đề:**
```c
// Bên trong printf()/LOG_DEBUG():
int printf(const char *fmt, ...) {
    char buffer[256];  // ← Chiếm stack!
    va_list args;
    va_start(args, fmt);
    vsnprintf(buffer, 256, fmt, args);  // ← Buffer lớn trên stack
    va_end(args);
    // ... send to UART ...
}
```

---

### ⭐ QUY TẮC #4: TRÁNH RECURSION
**Mức độ:** 🔴 CRITICAL

```c
/* ❌ CẤM TUYỆT ĐỐI */
void recursive_func(int depth) {
    if(depth <= 0) return;
    char buffer[64];  // 64 bytes × depth = OVERFLOW!
    recursive_func(depth - 1);
}

/* ✅ DÙNG LOOP THAY VÌ RECURSION */
void iterative_func(int max_depth) {
    for(int i = 0; i < max_depth; i++) {
        static char buffer[64];  // Chỉ 64 bytes, không nhân lên
        // ... process ...
    }
}
```

**Quy định:**
- ❌ **TUYỆT ĐỐI KHÔNG** dùng recursion trong embedded
- ✅ Luôn dùng loop thay cho recursion
- ✅ Nếu bắt buộc phải dùng recursion → giới hạn depth < 5

---

### ⭐ QUY TẮC #5: STRUCT TRÊN STACK
**Mức độ:** 🟠 HIGH

```c
/* ❌ NGUY HIỂM */
void process_gps(void) {
    struct tm time_struct;     // 56 bytes
    GPS_Data_t gps_snapshot;   // 50 bytes
    NTP_Packet_t ntp_packet;   // 48 bytes
    // Total: 154 bytes chỉ từ 3 struct!
}

/* ✅ AN TOÀN */
static struct tm g_time_struct;
static GPS_Data_t g_gps_snapshot;

void process_gps(void) {
    // Dùng global structs
}
```

**Quy định:**
- ❌ Struct > 32 bytes không để trên stack
- ✅ Dùng static/global cho struct lớn
- ✅ Truyền pointer thay vì copy struct

---

### ⭐ QUY TẮC #6: PASS BY REFERENCE
**Mức độ:** 🟡 MEDIUM

```c
/* ❌ TRÁNH - Copy toàn bộ struct lên stack */
void process_config(wiz_NetInfo config) {  // 16 bytes copied!
    // ... process ...
}

/* ✅ ĐÚNG - Chỉ copy pointer (4 bytes) */
void process_config(const wiz_NetInfo *config) {
    // ... process config->ip, config->gw ...
}
```

---

### ⭐ QUY TẮC #7: GIỚI HẠN STRING OPERATIONS
**Mức độ:** 🟠 HIGH

```c
/* ❌ NGUY HIỂM */
void parse_nmea(const char *sentence) {
    char temp[256];             // 256 bytes
    char field1[32], field2[32]; // 64 bytes
    sprintf(temp, "Processing: %s", sentence);  // sprintf buffer!
}

/* ✅ AN TOÀN */
void parse_nmea(const char *sentence) {
    static char temp[256];      // Static buffer
    // ... hoặc ...
    // Xử lý trực tiếp không cần temp buffer
}
```

**Quy định:**
- ❌ `sprintf()` trên local buffer > 64 bytes
- ✅ Dùng `snprintf()` với giới hạn rõ ràng
- ✅ Static buffer cho string manipulation

---

### ⭐ QUY TẮC #8: INLINE FUNCTIONS
**Mức độ:** 🟡 MEDIUM

```c
/* ❌ KHI INLINE, STACK TĂNG GẤP ĐÔI */
inline void helper1(void) {
    char buf[100];
    // ...
}
inline void helper2(void) {
    char buf[100];
    // ...
}
void caller(void) {
    helper1();  // Inline → buf[100] on stack
    helper2();  // Inline → buf[100] nữa!
    // Total: 200 bytes!
}

/* ✅ KHÔNG INLINE CHO HÀM CÓ BUFFER LỚN */
void helper1(void) {  // Không inline
    static char buf[100];
}
```

---

### ⭐ QUY TẮC #9: VA_ARGS FUNCTIONS
**Mức độ:** 🟠 HIGH

```c
/* ❌ NGUY HIỂM - Variadic functions tốn nhiều stack */
void my_log(const char *fmt, ...) {
    char buffer[256];  // Internal buffer
    va_list args;
    va_start(args, fmt);
    vsnprintf(buffer, 256, fmt, args);
    // ...
}

/* ✅ GIẢI PHÁP - Fixed arguments */
void my_log_fixed(const char *tag, const char *msg, int value) {
    printf("[%s] %s: %d\n", tag, msg, value);
}
```

---

### ⭐ QUY TẮC #10: NESTED FUNCTION CALLS
**Mức độ:** 🟠 HIGH

```c
/* ❌ MỖI HÀM THÊM STACK OVERHEAD */
void main(void) {
    system_main_loop();           // +32 bytes
}
void system_main_loop(void) {
    slaveClockRun();              // +32 bytes
}
void slaveClockRun(void) {
    oneSecondfucns();             // +32 bytes
}
void oneSecondfucns(void) {
    gps_once();                   // +32 bytes
}
void gps_once(void) {
    stable_frac_offset();         // +32 bytes
}
void stable_frac_offset(void) {
    LOG_DEBUG("...", ...);        // +256 bytes (printf buffer)
}
// Total: 32×5 + 256 = 416 bytes CHỈ TỪ CALL OVERHEAD!

/* ✅ GIẢM CALL DEPTH */
void main(void) {
    while(1) {
        // Inline logic trực tiếp thay vì gọi hàm sâu
        if(gps_every_sec) {
            // Handle GPS directly
        }
    }
}
```

---

### ⭐ QUY TẮC #11: COMPILER OPTIMIZATION
**Mức độ:** 🟡 MEDIUM

```c
/* Optimization levels ảnh hưởng stack usage:
 * -O0: Stack usage cao nhất (dễ debug)
 * -O1: Giảm 20-30%
 * -O2: Giảm 30-50% ✅ KHUYẾN NGHỊ
 * -Os: Stack nhỏ nhất (giảm ~50%)
 */
```

**Quy định:**
- ✅ Production build: `-O2` hoặc `-Os`
- ✅ Debug build: `-O0` nhưng tăng stack size
- ✅ Test với optimization level thực tế

---

### ⭐ QUY TẮC #12: WATCHDOG VÀ LONG OPERATIONS
**Mức độ:** 🟡 MEDIUM

```c
/* ❌ HÀM NÀY CÓ THỂ MẤT LÂU → STACK ACCUMULATES */
void gps_once(void) {
    stable_frac_offset();  // Mất 50ms
    LOG_DEBUG(...);         // Printf mất 20ms
    // Total: 70ms trong deep call stack!
}

/* ✅ BREAK INTO SMALLER CHUNKS */
void gps_once(void) {
    // Xử lý từng phần nhỏ
    stable_frac_offset();  // Phải nhanh < 10ms
    
    // Log sau, ở ngoài call stack sâu
    flag_need_log = 1;
}

void main_loop(void) {
    if(flag_need_log) {
        LOG_DEBUG(...);  // Gọi ở mức nông
        flag_need_log = 0;
    }
}
```

---

### ⭐ QUY TẮC #13: CONST DATA PLACEMENT
**Mức độ:** 🟡 MEDIUM

```c
/* ❌ STRING LITERAL TRÊN STACK (compiler dependent) */
void send_message(void) {
    const char *msg = "This is a very long message...";
    // Compiler có thể copy string lên stack!
}

/* ✅ STATIC CONST ĐẢM BẢO Ở FLASH */
static const char MSG[] = "This is a very long message...";
void send_message(void) {
    // Chỉ copy 4-byte pointer
}
```

---

### ⭐ QUY TẮC #14: INTERRUPTS VÀ STACK
**Mức độ:** 🔴 CRITICAL

```c
/* ⚠️  INTERRUPT CŨNG DÙNG STACK! */
void TIM3_IRQHandler(void) {
    // ISR execution dùng SAME stack như main!
    char buf[64];  // ❌ Thêm 64 bytes khi interrupt fire
    
    // Nếu interrupt fire khi main đang trong deep call:
    // main → func1 → func2 → func3 → ISR
    // Stack usage = main_stack + ISR_stack!
}

/* ✅ ISR PHẢI NHẸ NHẤT CÓ THỂ */
void TIM3_IRQHandler(void) {
    // Chỉ set flag, không xử lý logic
    flag = 1;
    counter++;
    // NO buffers, NO function calls!
}
```

**Quy định:**
- ❌ KHÔNG có local buffer trong ISR
- ❌ KHÔNG gọi hàm phức tạp từ ISR
- ✅ ISR chỉ set flag, xử lý ở main loop

---

### ⭐ QUY TẮC #15: TESTING STACK USAGE
**Mức độ:** 🔴 CRITICAL

```c
/* THÊM VÀO MAIN INIT */
void Stack_Init_Guard(void) {
    extern uint32_t _sstack;
    extern uint32_t _estack;
    
    uint32_t stack_size = (uint32_t)&_estack - (uint32_t)&_sstack;
    LOG_INFO("Stack", "Total stack: %u bytes", stack_size);
    
    // ⚠️  CẢNH BÁO NẾU STACK NHỎ
    if(stack_size < 2048) {
        LOG_ERROR("Stack", "⚠️  Stack size too small! Need >= 2048 bytes");
    }
}

/* THÊM VÀO CRITICAL FUNCTIONS */
void gps_once(void) {
    uint32_t sp;
    __asm volatile ("MOV %0, SP" : "=r" (sp));
    
    extern uint32_t _sstack;
    uint32_t stack_free = sp - (uint32_t)&_sstack;
    
    if(stack_free < 512) {
        LOG_ERROR("Stack", "⚠️  Only %u bytes free!", stack_free);
    }
    
    // ... rest of function ...
}
```

---

## 3. PATTERNS NGUY HIỂM PHẢI TRÁNH

### ❌ PATTERN #1: Deep Call với Printf

```c
/* VÍ DỤ THỰC TẾ TỪ PROJECT CỦA BẠN */
main()
  → system_main_loop()          // +32 bytes
    → slaveClockRun()           // +32 bytes
      → oneSecondfucns()        // +32 bytes
        → gps_once()            // +32 bytes
          → stable_frac_offset() // +32 bytes
            → LOG_DEBUG()       // +256 bytes (vsnprintf)
              
// TOTAL: 416 bytes CHỈ TỪ CALL CHAIN!
```

**FIX:**
```c
/* GIẢM CALL DEPTH - GỌI GPS LOGIC Ở NÔNG HƠN */
void oneSecondfucns(void) {
    // Xử lý GPS logic trực tiếp ở đây
    // Không gọi gps_once() → stable_frac_offset()
    
    if(gps_every_sec == 1) {
        // Inline logic của stable_frac_offset() vào đây
        DELTA_PPS_GPS_RTC = check_PPS_GPS;
        
        if(abs(DELTA_PPS_GPS_RTC) < 400) {
            if(stable_delta_pulse < 10) stable_delta_pulse++;
            unstable_delta_pulse = 0;
        } else {
            stable_delta_pulse = 0;
            if(unstable_delta_pulse < 10) unstable_delta_pulse++;
        }
        
        gps_every_sec = 0;
    }
}
```

---

### ❌ PATTERN #2: Multiple Large Buffers

```c
/* NGUY HIỂM */
void process_network(void) {
    uint8_t tx_buf[512];        // 512 bytes
    uint8_t rx_buf[512];        // 512 bytes
    char log_buf[256];          // 256 bytes
    // Total: 1280 bytes!
}
```

**FIX:**
```c
/* Static buffers shared */
static uint8_t g_tx_buf[512];
static uint8_t g_rx_buf[512];

void process_network(void) {
    // Chỉ dùng pointers
}
```

---

### ❌ PATTERN #3: String Building on Stack

```c
/* NGUY HIỂM */
void build_response(void) {
    char response[512];
    sprintf(response, "HTTP/1.1 200 OK\r\n");
    strcat(response, "Content-Type: text/html\r\n");
    strcat(response, webpage_content);  // Thêm nữa!
}
```

**FIX:**
```c
static char g_response[512];

void build_response(void) {
    snprintf(g_response, sizeof(g_response), 
             "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n%s",
             webpage_content);
}
```

---

## 4. STACK SAFETY CHECKLIST

### ✅ PRE-DEPLOYMENT CHECKLIST:

```markdown
[ ] Stack size >= 2048 bytes (check linker script)
[ ] Không có local array > 128 bytes
[ ] Không có recursion
[ ] Call depth < 7 levels
[ ] Printf/LOG_DEBUG có format string < 80 chars
[ ] ISR không có local buffers
[ ] ISR không gọi heavy functions
[ ] Test với compiler optimization (-O2)
[ ] Stack usage monitoring được bật
[ ] Watchdog timeout >= longest operation time
```

### ✅ CODE REVIEW CHECKLIST:

Khi review mỗi function, hỏi:

1. **Hàm này có local array không?**
   - Có → Size bao nhiêu? > 128 bytes → ❌ Fail

2. **Hàm này có gọi LOG_DEBUG/printf không?**
   - Có → Format string bao nhiêu args? > 5 → ❌ Fail

3. **Hàm này được gọi từ đâu?**
   - Call depth > 5 levels → ❌ Fail

4. **Hàm này có gọi hàm khác không?**
   - Có → Cộng dồn stack usage của tất cả

5. **Hàm này có thể chạy trong ISR không?**
   - Có → Phải minimal, no buffers

---

## 5. TOOLS VÀ DEBUG METHODS

### 🔧 METHOD 1: Compile-Time Stack Analysis

```bash
# Build với map file
arm-none-eabi-gcc -Wl,-Map=output.map ...

# Analyze stack usage
arm-none-eabi-nm --print-size --size-sort output.elf | grep " [bBdD] "

# GCC stack usage analysis
arm-none-eabi-gcc -fstack-usage ...
# Tạo file .su với stack usage mỗi function
```

---

### 🔧 METHOD 2: Runtime Stack Monitoring

```c
// Add to main.h
#define ENABLE_STACK_MONITOR

#ifdef ENABLE_STACK_MONITOR
extern uint32_t _sstack, _estack;

#define STACK_CHECK() do { \
    uint32_t sp; \
    __asm volatile ("MOV %0, SP" : "=r" (sp)); \
    uint32_t free = sp - (uint32_t)&_sstack; \
    if(free < 512) { \
        LOG_ERROR("Stack", "⚠️  %u bytes free in %s()!", free, __func__); \
    } \
} while(0)

#else
#define STACK_CHECK()
#endif

// Usage:
void critical_function(void) {
    STACK_CHECK();  // Auto check tại đầu hàm
    // ... code ...
}
```

---

### 🔧 METHOD 3: Stack Canary

```c
#define STACK_CANARY_SIZE 32
volatile uint32_t stack_canary[STACK_CANARY_SIZE/4] __attribute__((section(".noinit")));

void Stack_Canary_Init(void) {
    for(int i = 0; i < STACK_CANARY_SIZE/4; i++) {
        stack_canary[i] = 0xDEADBEEF;
    }
}

uint8_t Stack_Canary_Check(void) {
    for(int i = 0; i < STACK_CANARY_SIZE/4; i++) {
        if(stack_canary[i] != 0xDEADBEEF) {
            LOG_ERROR("Stack", "Canary corrupted at %d!", i);
            return 0;
        }
    }
    return 1;
}
```

---

### 🔧 METHOD 4: MPU Stack Guard

```c
void MPU_Configure_Stack_Guard(void) {
    extern uint32_t _sstack;
    
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // Protect 256 bytes at stack bottom
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = (uint32_t)&_sstack;
    MPU_InitStruct.Size = MPU_REGION_SIZE_256B;
    MPU_InitStruct.AccessPermission = MPU_REGION_NO_ACCESS;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}

// ISR sẽ fire khi stack overflow
void MemManage_Handler(void) {
    LOG_ERROR("MPU", "Stack overflow detected!");
    // Log và reset
}
```

---

## 📊 STACK SIZE RECOMMENDATIONS

| System Type | Minimum Stack | Recommended | With Debug Logging |
|-------------|---------------|-------------|-------------------|
| Simple (no networking) | 1024 bytes | 1536 bytes | 2048 bytes |
| With Networking | 1536 bytes | 2048 bytes | 3072 bytes |
| Complex (GPS+NTP+HTTP) | 2048 bytes | 3072 bytes | 4096 bytes |
| With printf/sprintf | +512 bytes per nested printf | | |

**Công thức tính:**
```
Stack_Size = Base_Usage + (Call_Depth × 32) + Max_Local_Buffers + (N_Printfs × 256)

Ví dụ project của bạn:
- Base: 512 bytes
- Call depth: 6 levels × 32 = 192 bytes
- Max buffers: 256 bytes (LOG_DEBUG)
- Printfs: 2 nested × 256 = 512 bytes
Total: 512 + 192 + 256 + 512 = 1472 bytes

→ Cần ít nhất 2048 bytes để an toàn!
```

---

## 🎯 KHUYẾN NGHỊ CỤ THỂ CHO PROJECT CỦA BẠN

### 1. IMMEDIATE FIX cho `stable_frac_offset()`:

```c
/* Option A: Inline logic vào oneSecondfucns() */
void oneSecondfucns(void) {
    if(gps_every_sec == 1) {
        // Inline stable_frac_offset() logic here
        if(slave_clock.work_mode != GPS_MODE) {
            gps_every_sec = 0;
            return;
        }
        
        DELTA_PPS_GPS_RTC = check_PPS_GPS;
        // ... rest of logic ...
        
        gps_every_sec = 0;
    }
}

/* Option B: Gọi ở main loop thay vì từ gps_once() */
void system_main_loop(void) {
    slaveClockRun();
    
    // Xử lý GPS ở đây (shallow call)
    if(gps_every_sec == 1) {
        stable_frac_offset();  // Gọi trực tiếp từ main loop
        gps_every_sec = 0;
    }
}
```

### 2. GIẢM CALL DEPTH:

```c
/* TRƯỚC (7 cấp): */
main → system_main_loop → slaveClockRun → oneSecondfucns → 
       gps_once → stable_frac_offset → LOG_DEBUG

/* SAU (4 cấp): */
main → system_main_loop → handle_gps_direct → LOG_DEBUG
```

### 3. TĂNG STACK SIZE:

Tìm file `.ld` (linker script) và sửa:

```ld
/* TRƯỚC */
_Min_Stack_Size = 0x400; /* 1024 bytes - TOO SMALL! */

/* SAU */
_Min_Stack_Size = 0x800; /* 2048 bytes - SAFE */
```

### 4. THÊM MONITORING:

```c
// Thêm vào main.c
void main(void) {
    HAL_Init();
    Stack_Canary_Init();  // ← Add this
    
    // ... init code ...
    
    while(1) {
        system_main_loop();
        
        // Check mỗi 10s
        static uint32_t check_timer = 0;
        if(HAL_GetTick() - check_timer > 10000) {
            if(!Stack_Canary_Check()) {
                LOG_ERROR("Main", "Stack overflow!");
                NVIC_SystemReset();
            }
            check_timer = HAL_GetTick();
        }
    }
}
```

---

## 📝 TÓM TẮT - ƯU TIÊN THỰC HIỆN

### 🔴 PRIORITY 1 (Làm ngay):
1. ✅ Giảm call depth: Inline `stable_frac_offset()` vào `oneSecondfucns()`
2. ✅ Tăng stack size lên >= 2048 bytes trong linker script
3. ✅ Thêm stack monitoring code

### 🟠 PRIORITY 2 (Tuần này):
1. ✅ Review tất cả hàm có local array > 128 bytes → chuyển sang static
2. ✅ Giảm LOG_DEBUG format string xuống < 80 chars
3. ✅ Test với -O2 optimization

### 🟡 PRIORITY 3 (Tuần sau):
1. ✅ Implement MPU stack guard
2. ✅ Add compile-time stack analysis
3. ✅ Tạo stack usage report

---

## 🆘 KHI NÀO CẦN HELP?

Nếu sau khi áp dụng các quy tắc trên mà vẫn gặp vấn đề:

1. Cung cấp:
   - Linker script (file .ld)
   - Map file (output.map)
   - Stack usage files (*.su)
   - Call stack tại thời điểm crash

2. Run stack monitoring và gửi log:
   ```
   [Stack] SP=0x20003xxx, Free=xxx bytes
   ```

3. Build với debug symbols và gửi assembly listing

---

**END OF DOCUMENT**
