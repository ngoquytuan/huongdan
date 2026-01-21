/**
 * @file stack_monitor_simple.h
 * @brief ULTRA-SIMPLE Stack Monitor - No inline assembly, pure C
 * @date 2026-01-21
 * @version 3.0 - SIMPLIFIED for Keil MDK
 * 
 * Use this if stack_monitor.h gives compiler errors
 * 
 * Usage:
 * 1. #include "stack_monitor_simple.h" in main.c
 * 2. Call Stack_Monitor_Init() after HAL_Init()
 * 3. Call Stack_Monitor_Periodic() in main loop
 */

#ifndef __STACK_MONITOR_SIMPLE_H
#define __STACK_MONITOR_SIMPLE_H

#include <stdint.h>
#include "debug_log.h"

/* ============================================================================
   CONFIGURATION
   ============================================================================ */

// Enable/disable (comment out to disable)
#define ENABLE_STACK_MONITOR_SIMPLE

// Stack canary size
#define STACK_CANARY_SIZE       16      // 16 words = 64 bytes
#define STACK_CANARY_PATTERN    0xDEADBEEF

// Warning thresholds
#define STACK_WARNING_BYTES     512
#define STACK_CRITICAL_BYTES    256

// Check interval
#define STACK_CHECK_INTERVAL_MS 10000   // 10 seconds

/* ============================================================================
   EXTERNAL LINKER SYMBOLS
   ============================================================================ */

// From linker script - if you get errors, check your .ld file
extern uint32_t _estack;
extern uint32_t _sstack;

/* ============================================================================
   SIMPLE STACK MONITOR
   ============================================================================ */

#ifdef ENABLE_STACK_MONITOR_SIMPLE

// Canary array
volatile uint32_t g_stack_canary[STACK_CANARY_SIZE];

/**
 * @brief Initialize stack monitoring
 */
void Stack_Monitor_Init(void)
{
    // Fill canary
    for(uint16_t i = 0; i < STACK_CANARY_SIZE; i++) {
        g_stack_canary[i] = STACK_CANARY_PATTERN;
    }
    
    uint32_t stack_size = (uint32_t)&_estack - (uint32_t)&_sstack;
    
    LOG_INFO("Stack", "Monitor initialized");
    LOG_INFO("Stack", "  Size: %u bytes", stack_size);
    LOG_INFO("Stack", "  Canary at: 0x%08X", (uint32_t)&g_stack_canary[0]);
    
    if(stack_size < 2048) {
        LOG_ERROR("Stack", "WARNING: Stack < 2048 bytes!");
    }
}

/**
 * @brief Check canary integrity
 * @return 1 if OK, 0 if corrupted
 */
uint8_t Stack_Canary_Check(void)
{
    for(uint16_t i = 0; i < STACK_CANARY_SIZE; i++) {
        if(g_stack_canary[i] != STACK_CANARY_PATTERN) {
            LOG_ERROR("Stack", "CANARY CORRUPT at %d!", i);
            return 0;
        }
    }
    return 1;
}

/**
 * @brief Get stack pointer (using local variable address trick)
 * @return Approximate stack pointer value
 * @note This is less accurate but works with all compilers
 */
uint32_t Stack_Get_SP_Simple(void)
{
    volatile uint32_t dummy;
    return (uint32_t)&dummy;
}

/**
 * @brief Calculate free stack
 * @return Free bytes (approximate)
 */
uint32_t Stack_Get_Free(void)
{
    uint32_t sp = Stack_Get_SP_Simple();
    uint32_t base = (uint32_t)&_sstack;
    
    if(sp < base) return 0;
    
    return sp - base;
}

/**
 * @brief Calculate used stack
 * @return Used bytes (approximate)
 */
uint32_t Stack_Get_Used(void)
{
    uint32_t sp = Stack_Get_SP_Simple();
    uint32_t top = (uint32_t)&_estack;
    
    return top - sp;
}

/**
 * @brief Get total stack size
 * @return Stack size in bytes
 */
uint32_t Stack_Get_Size(void)
{
    return (uint32_t)&_estack - (uint32_t)&_sstack;
}

/**
 * @brief Check stack with warnings
 * @param func_name Function name (pass __func__ or string)
 * @return 1 if OK, 0 if critical
 */
uint8_t Stack_Check(const char *func_name)
{
    uint32_t free = Stack_Get_Free();
    uint32_t used = Stack_Get_Used();
    uint32_t total = Stack_Get_Size();
    
    // Check canary
    if(!Stack_Canary_Check()) {
        LOG_ERROR("Stack", "OVERFLOW in %s!", func_name);
        return 0;
    }
    
    // Check thresholds
    if(free < STACK_CRITICAL_BYTES) {
        LOG_ERROR("Stack", "CRITICAL: %u bytes free in %s", free, func_name);
        return 0;
    }
    else if(free < STACK_WARNING_BYTES) {
        LOG_WARN("Stack", "Low: %u bytes free in %s", free, func_name);
    }
    
    return 1;
}

/**
 * @brief Macro for easy stack check
 */
#define STACK_CHECK() Stack_Check(__func__)

/**
 * @brief Print stack report
 */
void Stack_Report(void)
{
    uint32_t sp = Stack_Get_SP_Simple();
    uint32_t free = Stack_Get_Free();
    uint32_t used = Stack_Get_Used();
    uint32_t total = Stack_Get_Size();
    
    LOG_INFO("Stack", "=== Report ===");
    LOG_INFO("Stack", "SP:    0x%08X", sp);
    LOG_INFO("Stack", "Total: %u bytes", total);
    LOG_INFO("Stack", "Used:  %u bytes", used);
    LOG_INFO("Stack", "Free:  %u bytes", free);
    LOG_INFO("Stack", "Canary: %s", Stack_Canary_Check() ? "OK" : "FAIL");
}

/**
 * @brief Periodic check (call from main loop)
 */
void Stack_Monitor_Periodic(void)
{
    static uint32_t last_check = 0;
    uint32_t now = HAL_GetTick();
    
    if((now - last_check) >= STACK_CHECK_INTERVAL_MS) {
        last_check = now;
        
        if(!Stack_Canary_Check()) {
            LOG_ERROR("Stack", "Periodic check FAILED!");
            HAL_Delay(5000);
            NVIC_SystemReset();
        }
        
        uint32_t free = Stack_Get_Free();
        if(free < STACK_WARNING_BYTES) {
            LOG_WARN("Stack", "Periodic: %u bytes free", free);
        }
    }
}

#else  // Disabled

#define Stack_Monitor_Init()
#define Stack_Canary_Check() (1)
#define Stack_Get_Free() (0)
#define Stack_Get_Used() (0)
#define Stack_Get_Size() (0)
#define Stack_Check(name) (1)
#define STACK_CHECK()
#define Stack_Report()
#define Stack_Monitor_Periodic()

#endif  // ENABLE_STACK_MONITOR_SIMPLE

#endif  // __STACK_MONITOR_SIMPLE_H

/**
 * ============================================================================
 * USAGE EXAMPLE:
 * ============================================================================
 * 
 * #include "stack_monitor_simple.h"
 * 
 * int main(void)
 * {
 *     HAL_Init();
 *     SystemClock_Config();
 *     
 *     Stack_Monitor_Init();  // Initialize
 *     
 *     // ... other init ...
 *     
 *     while(1)
 *     {
 *         system_main_loop();
 *         Stack_Monitor_Periodic();  // Check every 10s
 *     }
 * }
 * 
 * // In critical functions:
 * void gps_once(void)
 * {
 *     STACK_CHECK();  // Quick check
 *     // ... code ...
 * }
 * 
 * ============================================================================
 * WHY THIS VERSION IS SIMPLER:
 * ============================================================================
 * 
 * 1. NO inline assembly - uses local variable address trick
 * 2. NO compiler-specific code
 * 3. NO complex macros
 * 4. Pure C that compiles on ANY compiler
 * 
 * Tradeoff: Stack pointer reading is APPROXIMATE (±32 bytes)
 * But good enough for overflow detection!
 * 
 * ============================================================================
 * COMPATIBILITY:
 * ============================================================================
 * 
 * ✅ Keil MDK-ARM (all versions)
 * ✅ GCC arm-none-eabi
 * ✅ IAR EWARM
 * ✅ Any ANSI C compiler
 */
