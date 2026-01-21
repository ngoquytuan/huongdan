/**
 * @file stack_monitor.h
 * @brief Stack overflow detection and monitoring utilities
 * @date 2026-01-21
 * @version 2.0 - Compatible with GCC, Keil, IAR
 * 
 * @note Add to your project to detect stack overflow issues
 * 
 * Usage:
 * 1. Include this header in main.c
 * 2. Call Stack_Monitor_Init() after HAL_Init()
 * 3. Call Stack_Monitor_Check() in critical functions
 * 4. Call Stack_Monitor_Periodic() in main loop
 */

#ifndef __STACK_MONITOR_H
#define __STACK_MONITOR_H

#include <stdint.h>
#include "debug_log.h"

/* ============================================================================
   CONFIGURATION
   ============================================================================ */
   
// Enable/disable stack monitoring (comment out for production)
#define ENABLE_STACK_MONITOR

// Stack canary configuration
#define STACK_CANARY_SIZE       64      // Bytes at stack bottom to protect
#define STACK_CANARY_PATTERN    0xDEADBEEF

// Warning thresholds
#define STACK_WARNING_THRESHOLD 512     // Warn if < 512 bytes free
#define STACK_CRITICAL_THRESHOLD 256    // Critical if < 256 bytes free

// Periodic check interval (ms)
#define STACK_CHECK_INTERVAL_MS 10000   // Check every 10 seconds

/* ============================================================================
   EXTERNAL SYMBOLS FROM LINKER SCRIPT
   ============================================================================ */
   
// These symbols are defined in your .ld linker script
// If you get linker errors, check your .ld file
extern uint32_t _estack;  // Top of stack (highest address)
extern uint32_t _sstack;  // Bottom of stack (lowest address)

/* ============================================================================
   COMPILER-INDEPENDENT STACK POINTER ACCESS
   ============================================================================ */

/**
 * @brief Get current stack pointer value (works with all compilers)
 * @return Current SP register value
 */
static inline uint32_t Stack_Get_SP(void)
{
    uint32_t sp;
    
    // Method 1: Try CMSIS intrinsic (most portable)
    #if defined(__CORTEX_M)
        // CMSIS function works with GCC, Keil, IAR
        sp = __get_MSP();  // Get Main Stack Pointer
    #else
        // Method 2: Compiler-specific inline assembly
        #if defined(__GNUC__) && !defined(__ARMCC_VERSION)
            // GCC compiler (arm-none-eabi-gcc)
            __asm volatile ("MOV %0, SP" : "=r" (sp));
            
        #elif defined(__ARMCC_VERSION)
            // Keil ARM Compiler
            #if (__ARMCC_VERSION >= 6000000)
                // ARM Compiler 6 (armclang) - uses GCC syntax
                __asm volatile ("MOV %0, SP" : "=r" (sp));
            #else
                // ARM Compiler 5 (armcc) - uses Keil syntax
                register uint32_t stack_ptr __asm("sp");
                sp = stack_ptr;
            #endif
            
        #elif defined(__ICCARM__)
            // IAR compiler
            sp = __get_MSP();
            
        #else
            #error "Unsupported compiler! Add Stack_Get_SP() implementation for your toolchain"
        #endif
    #endif
    
    return sp;
}

/* ============================================================================
   STACK CANARY PROTECTION
   ============================================================================ */

#ifdef ENABLE_STACK_MONITOR

// Canary array placed at known location
// Use __attribute__((section(".noinit"))) to prevent .bss clearing
#if defined(__GNUC__)
    volatile uint32_t g_stack_canary[STACK_CANARY_SIZE / sizeof(uint32_t)] 
                      __attribute__((section(".noinit")));
#elif defined(__ARMCC_VERSION)
    // Keil doesn't support .noinit section the same way
    // Just use regular .bss (will be cleared at startup)
    volatile uint32_t g_stack_canary[STACK_CANARY_SIZE / sizeof(uint32_t)];
#else
    volatile uint32_t g_stack_canary[STACK_CANARY_SIZE / sizeof(uint32_t)];
#endif

/**
 * @brief Initialize stack canary protection
 * @note Call once at startup, after HAL_Init()
 */
static inline void Stack_Monitor_Init(void)
{
    // Fill canary with known pattern
    for(uint16_t i = 0; i < (STACK_CANARY_SIZE / sizeof(uint32_t)); i++) {
        g_stack_canary[i] = STACK_CANARY_PATTERN;
    }
    
    uint32_t stack_size = (uint32_t)&_estack - (uint32_t)&_sstack;
    
    LOG_INFO("Stack", "Monitor initialized");
    LOG_INFO("Stack", "  Base:   0x%08X", (uint32_t)&_sstack);
    LOG_INFO("Stack", "  Top:    0x%08X", (uint32_t)&_estack);
    LOG_INFO("Stack", "  Size:   %u bytes", stack_size);
    LOG_INFO("Stack", "  Canary: 0x%08X (%u bytes)", 
             (uint32_t)&g_stack_canary[0], STACK_CANARY_SIZE);
    
    // Warning if stack too small
    if(stack_size < 2048) {
        LOG_ERROR("Stack", "Stack size < 2048 bytes! Risk of overflow!");
    }
}

/**
 * @brief Check if stack canary is intact
 * @return 1 if OK, 0 if corrupted (stack overflow detected)
 */
static inline uint8_t Stack_Canary_Check(void)
{
    for(uint16_t i = 0; i < (STACK_CANARY_SIZE / sizeof(uint32_t)); i++) {
        if(g_stack_canary[i] != STACK_CANARY_PATTERN) {
            LOG_ERROR("Stack", "CANARY CORRUPTED at index %d!", i);
            LOG_ERROR("Stack", "   Expected: 0x%08X", STACK_CANARY_PATTERN);
            LOG_ERROR("Stack", "   Got:      0x%08X", g_stack_canary[i]);
            return 0;  // Stack overflow detected!
        }
    }
    return 1;  // Canary intact
}

/**
 * @brief Calculate free stack space
 * @return Free bytes remaining on stack
 */
static inline uint32_t Stack_Get_Free(void)
{
    uint32_t sp = Stack_Get_SP();
    uint32_t stack_base = (uint32_t)&_sstack;
    
    if(sp < stack_base) {
        // Stack pointer below base - serious overflow!
        return 0;
    }
    
    return sp - stack_base;
}

/**
 * @brief Calculate used stack space
 * @return Bytes of stack currently used
 */
static inline uint32_t Stack_Get_Used(void)
{
    uint32_t sp = Stack_Get_SP();
    uint32_t stack_top = (uint32_t)&_estack;
    
    return stack_top - sp;
}

/**
 * @brief Get total stack size
 * @return Total stack size in bytes
 */
static inline uint32_t Stack_Get_Size(void)
{
    return (uint32_t)&_estack - (uint32_t)&_sstack;
}

/**
 * @brief Check stack usage and log warnings
 * @param function_name Name of calling function (use __func__)
 * @return 1 if OK, 0 if critical
 */
static inline uint8_t Stack_Monitor_Check_With_Name(const char *function_name)
{
    uint32_t free = Stack_Get_Free();
    uint32_t used = Stack_Get_Used();
    uint32_t total = Stack_Get_Size();
    uint32_t sp = Stack_Get_SP();
    
    // Check canary first
    if(!Stack_Canary_Check()) {
        LOG_ERROR("Stack", "OVERFLOW in %s()!", function_name);
        LOG_ERROR("Stack", "   SP:   0x%08X", sp);
        LOG_ERROR("Stack", "   Used: %u/%u bytes", used, total);
        return 0;
    }
    
    // Check thresholds
    if(free < STACK_CRITICAL_THRESHOLD) {
        LOG_ERROR("Stack", "CRITICAL: Only %u bytes free in %s()!", 
                  free, function_name);
        LOG_ERROR("Stack", "   SP:   0x%08X", sp);
        LOG_ERROR("Stack", "   Used: %u/%u bytes", used, total);
        return 0;
    }
    else if(free < STACK_WARNING_THRESHOLD) {
        LOG_WARN("Stack", "Low stack: %u bytes free in %s()", 
                 free, function_name);
        LOG_WARN("Stack", "   SP:   0x%08X", sp);
        LOG_WARN("Stack", "   Used: %u/%u bytes", used, total);
    }
    
    return 1;
}

/**
 * @brief Macro to check stack in current function
 * @note Automatically uses __func__ for function name
 */
#define STACK_CHECK() Stack_Monitor_Check_With_Name(__func__)

/**
 * @brief Detailed stack report (for debugging)
 */
static inline void Stack_Monitor_Report(void)
{
    uint32_t sp = Stack_Get_SP();
    uint32_t free = Stack_Get_Free();
    uint32_t used = Stack_Get_Used();
    uint32_t total = Stack_Get_Size();
    
    LOG_INFO("Stack", "=== Stack Report ===");
    LOG_INFO("Stack", "  Base:     0x%08X", (uint32_t)&_sstack);
    LOG_INFO("Stack", "  Top:      0x%08X", (uint32_t)&_estack);
    LOG_INFO("Stack", "  Current:  0x%08X", sp);
    LOG_INFO("Stack", "  Total:    %u bytes", total);
    LOG_INFO("Stack", "  Used:     %u bytes", used);
    LOG_INFO("Stack", "  Free:     %u bytes", free);
    LOG_INFO("Stack", "  Canary:   %s", 
             Stack_Canary_Check() ? "OK" : "CORRUPTED");
}

/**
 * @brief Periodic stack check (call from main loop)
 * @note Uses static timer, checks every STACK_CHECK_INTERVAL_MS
 */
static inline void Stack_Monitor_Periodic(void)
{
    static uint32_t last_check = 0;
    uint32_t now = HAL_GetTick();
    
    if((now - last_check) >= STACK_CHECK_INTERVAL_MS) {
        last_check = now;
        
        if(!Stack_Canary_Check()) {
            LOG_ERROR("Stack", "Periodic check failed! Resetting...");
            HAL_Delay(5000);  // Give time to log
            NVIC_SystemReset();
        }
        
        // Optional: Full report every check
        // Stack_Monitor_Report();
        
        uint32_t free = Stack_Get_Free();
        if(free < STACK_WARNING_THRESHOLD) {
            LOG_WARN("Stack", "Periodic: %u bytes free", free);
        }
    }
}

#else  // ENABLE_STACK_MONITOR not defined

// No-op stubs when monitoring disabled
#define Stack_Monitor_Init()
#define Stack_Canary_Check() (1)
#define Stack_Get_SP() (0)
#define Stack_Get_Free() (0)
#define Stack_Get_Used() (0)
#define Stack_Get_Size() (0)
#define Stack_Monitor_Check_With_Name(name) (1)
#define STACK_CHECK()
#define Stack_Monitor_Report()
#define Stack_Monitor_Periodic()

#endif  // ENABLE_STACK_MONITOR

/* ============================================================================
   STACK PAINT & WATERMARK (Advanced usage)
   ============================================================================ */

#ifdef ENABLE_STACK_MONITOR

#define STACK_FILL_PATTERN 0xA5A5A5A5

/**
 * @brief Fill unused stack with pattern (call early in main)
 * @note This helps measure maximum stack usage
 */
static inline void Stack_Paint(void)
{
    uint32_t current_sp = Stack_Get_SP();
    
    // Fill from stack bottom to current SP
    volatile uint32_t *ptr = (uint32_t *)&_sstack;
    
    while((uint32_t)ptr < current_sp) {
        *ptr++ = STACK_FILL_PATTERN;
    }
    
    LOG_INFO("Stack", "Stack painted with pattern 0x%08X", STACK_FILL_PATTERN);
}

/**
 * @brief Measure maximum stack usage since Stack_Paint()
 * @return Maximum bytes used (high water mark)
 */
static inline uint32_t Stack_Get_Max_Usage(void)
{
    // Count from bottom up, find first non-pattern byte
    volatile uint32_t *ptr = (uint32_t *)&_sstack;
    uint32_t untouched = 0;
    
    while(*ptr == STACK_FILL_PATTERN && (uint32_t)ptr < (uint32_t)&_estack) {
        ptr++;
        untouched += sizeof(uint32_t);
    }
    
    uint32_t total = Stack_Get_Size();
    uint32_t max_used = total - untouched;
    
    LOG_INFO("Stack", "Max usage: %u/%u bytes", max_used, total);
    
    return max_used;
}

#else

#define Stack_Paint()
#define Stack_Get_Max_Usage() (0)

#endif  // ENABLE_STACK_MONITOR

#endif  // __STACK_MONITOR_H

/**
 * USAGE EXAMPLE IN main.c:
 * ========================
 * 
 * #include "stack_monitor.h"
 * 
 * int main(void)
 * {
 *     HAL_Init();
 *     SystemClock_Config();
 *     
 *     // Initialize stack monitoring
 *     Stack_Monitor_Init();
 *     
 *     // Optional: Paint stack for watermark measurement
 *     Stack_Paint();
 *     
 *     // ... rest of initialization ...
 *     
 *     while(1) {
 *         system_main_loop();
 *         
 *         // Periodic stack check
 *         Stack_Monitor_Periodic();
 *     }
 * }
 * 
 * 
 * USAGE IN CRITICAL FUNCTIONS:
 * ============================
 * 
 * void gps_once(void)
 * {
 *     STACK_CHECK();  // Auto-check at function entry
 *     
 *     // ... rest of code ...
 * }
 * 
 * void stable_frac_offset(void)
 * {
 *     STACK_CHECK();
 *     
 *     // ... rest of code ...
 * }
 * 
 * 
 * COMPILER COMPATIBILITY:
 * =======================
 * 
 * This version supports:
 * - GCC (arm-none-eabi-gcc)
 * - Keil ARM Compiler 5 (armcc)
 * - Keil ARM Compiler 6 (armclang)
 * - IAR EWARM
 * 
 * Uses CMSIS __get_MSP() function which is standard across all compilers
 */
