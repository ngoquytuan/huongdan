# Stack Overflow Detection & Mitigation

## The Silent Killer

Stack overflow in embedded systems often manifests as:
- **Intermittent crashes** that are hard to reproduce
- **Random variable corruption** (especially globals near stack region)
- **Function return address corruption** leading to hard faults
- **Webpage features disappearing** while other functions work fine

Unlike desktop systems with memory protection, embedded MCUs allow stack to silently overflow into data/heap regions.

## Root Causes

### Cause 1: Deep Function Call Chains

**🔴 DANGER ZONE:**
```c
void main(void) {
    level_1();  // Stack frame: 32 bytes
}

void level_1(void) {
    char buffer[64];  // +64 bytes
    level_2();
}

void level_2(void) {
    uint8_t data[128];  // +128 bytes
    level_3();
}

void level_3(void) {
    char temp[256];  // +256 bytes
    level_4();
}

void level_4(void) {
    // Total stack usage: 32 + 64 + 128 + 256 = 480+ bytes
    // Plus function overhead, registers saved = easily 600+ bytes
}
```

**Why it fails:** STM32G474 typical stack size is 1-4KB. Deep call chains rapidly consume available stack.

**✅ CORRECT FIX:**
```c
// Flatten call hierarchy
void main(void) {
    process_step_1();  // Each function returns before next
    process_step_2();
    process_step_3();
    process_step_4();
}

// Move large buffers to static/global
static char shared_buffer[256];

void process_step_1(void) {
    // Use shared_buffer instead of local
    memset(shared_buffer, 0, sizeof(shared_buffer));
}
```

### Cause 2: Large Local Arrays

**🔴 DANGER ZONE:**
```c
void generate_webpage(void) {
    char html_buffer[2048];  // ❌ 2KB on stack!
    
    sprintf(html_buffer, "<html><head>...");
    send_http_response(html_buffer);
}
```

**Symptom observed:** Webpage loading works fine initially, then suddenly stops working while LED display and NTP continue functioning.

**Why it fails:** The 2KB buffer overflows into global variables that control webpage generation, corrupting them selectively.

**✅ CORRECT FIX:**
```c
// Use static storage (BSS section, not stack)
static char html_buffer[2048];

void generate_webpage(void) {
    memset(html_buffer, 0, sizeof(html_buffer));
    sprintf(html_buffer, "<html><head>...");
    send_http_response(html_buffer);
}
```

**Alternative: Dynamic allocation (if heap available):**
```c
void generate_webpage(void) {
    char *html_buffer = malloc(2048);
    if (html_buffer == NULL) return;
    
    sprintf(html_buffer, "<html><head>...");
    send_http_response(html_buffer);
    
    free(html_buffer);
}
```

### Cause 3: Printf/Sprintf with Many Arguments

**🔴 DANGER ZONE:**
```c
void log_gps_data(void) {
    // ❌ Each argument pushed to stack
    sprintf(buffer, 
        "GPS: %d/%d/%d %d:%d:%d lat=%ld lon=%ld alt=%d sat=%d hdop=%d fix=%c",
        year, month, day,          // 3 args
        hour, minute, second,      // 3 args
        latitude, longitude,       // 2 args (32-bit)
        altitude, satellites,      // 2 args
        hdop, fix_quality         // 2 args
    );
    // Total: 12+ arguments = ~48+ bytes stack just for args
    // Plus format string parsing, temporary buffers = 200+ bytes!
}
```

**Why it fails:** Variable argument functions (...) push all arguments to stack. Format string parsing allocates temporary buffers.

**✅ CORRECT FIX - Split Calls:**
```c
void log_gps_data(void) {
    // ✅ Multiple smaller calls
    sprintf(buffer, "GPS: %d/%d/%d %d:%d:%d", 
        year, month, day, hour, minute, second);
    
    strcat(buffer, " lat=");
    sprintf(temp, "%ld", latitude);
    strcat(buffer, temp);
    
    strcat(buffer, " lon=");
    sprintf(temp, "%ld", longitude);
    strcat(buffer, temp);
    
    sprintf(temp, " alt=%d sat=%d", altitude, satellites);
    strcat(buffer, temp);
}
```

**Alternative: Custom formatting:**
```c
void append_number(char *buf, int32_t value) {
    char temp[12];
    int i = 0;
    
    if (value < 0) {
        *buf++ = '-';
        value = -value;
    }
    
    do {
        temp[i++] = '0' + (value % 10);
        value /= 10;
    } while (value > 0);
    
    while (i > 0) {
        *buf++ = temp[--i];
    }
    *buf = '\0';
}
```

### Cause 4: Recursive Functions

**🔴 NEVER ALLOWED IN EMBEDDED:**
```c
void parse_json(char *json, int depth) {
    if (depth > 10) return;
    
    // ❌ WRONG: Recursion in embedded systems
    if (is_nested_object(json)) {
        parse_json(next_level, depth + 1);  // Unbounded stack usage!
    }
}
```

**✅ CORRECT FIX - Iterative:**
```c
#define MAX_DEPTH 10

void parse_json(char *json) {
    struct {
        char *ptr;
        int level;
    } stack[MAX_DEPTH];
    
    int stack_ptr = 0;
    stack[stack_ptr++] = (struct){json, 0};
    
    while (stack_ptr > 0) {
        struct item = stack[--stack_ptr];
        
        if (is_nested_object(item.ptr) && item.level < MAX_DEPTH) {
            stack[stack_ptr++] = (struct){next_level, item.level + 1};
        }
    }
}
```

## Detection Techniques

### Method 1: Static Analysis with GCC

Enable stack usage reporting in Keil/GCC:
```bash
# Add to compiler flags
-fstack-usage

# Generates .su files showing stack usage per function
grep -v "^#" *.su | sort -k2 -n -r | head -20
```

Example output:
```
httpServer.c:123:generate_webpage    2048    static
gps.c:456:parse_nmea_sentence        512     static
ntpClient.c:234:process_ntp          384     dynamic
main.c:89:main_loop                  128     static
```

**Interpretation:**
- `static`: Stack usage is deterministic
- `dynamic`: Stack usage varies (due to variable-length arrays, alloca, or recursion)
- **RED FLAG:** Any function >256 bytes needs review
- **CRITICAL:** Any `dynamic` marking requires immediate investigation

### Method 2: Runtime Stack Watermarking

```c
// In startup code
void fill_stack_canary(void) {
    extern uint32_t _estack;     // Top of stack (from linker)
    extern uint32_t _Min_Stack_Size;  // Minimum stack size
    
    uint32_t *stack_ptr = &_estack - (_Min_Stack_Size / 4);
    
    // Fill unused stack with known pattern
    for (uint32_t i = 0; i < (_Min_Stack_Size / 4); i++) {
        stack_ptr[i] = 0xDEADBEEF;
    }
}

// In idle task or periodic check
uint32_t check_stack_usage(void) {
    extern uint32_t _estack;
    extern uint32_t _Min_Stack_Size;
    
    uint32_t *stack_ptr = &_estack - (_Min_Stack_Size / 4);
    uint32_t unused = 0;
    
    // Count untouched words
    for (uint32_t i = 0; i < (_Min_Stack_Size / 4); i++) {
        if (stack_ptr[i] == 0xDEADBEEF) {
            unused++;
        } else {
            break;  // Stack has been used beyond this point
        }
    }
    
    uint32_t used_bytes = _Min_Stack_Size - (unused * 4);
    uint32_t percent = (used_bytes * 100) / _Min_Stack_Size;
    
    DEBUG_LOG("[STACK] Used: %lu/%lu bytes (%lu%%)", 
        used_bytes, _Min_Stack_Size, percent);
    
    return used_bytes;
}
```

### Method 3: Debugger Stack Profiling

In Keil uVision:
```
1. Set breakpoint in target function
2. View → Memory Windows → Memory 1
3. View stack pointer region: &__stack
4. Monitor SP register before/after calls
5. Calculate delta = max_sp - min_sp
```

In GDB:
```gdb
# Set hardware breakpoint
break function_name

# Print stack pointer
p $sp

# Continue and monitor
c

# Calculate difference
p $sp_before - $sp_after
```

### Method 4: Automated Scanner Script

```python
#!/usr/bin/env python3
import re
import sys

def scan_for_stack_risks(filepath):
    """Scan C file for stack overflow risks"""
    risks = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Pattern 1: Large local arrays
        match = re.search(r'(char|uint8_t|int|uint32_t)\s+\w+\[(\d+)\]', line)
        if match and int(match.group(2)) > 64:
            risks.append((i, f"Large array [{match.group(2)}]", line.strip()))
        
        # Pattern 2: Printf with many %
        if 'printf' in line or 'sprintf' in line:
            percent_count = line.count('%') - line.count('%%')
            if percent_count > 5:
                risks.append((i, f"Printf with {percent_count} args", line.strip()))
        
        # Pattern 3: Recursion
        func_match = re.search(r'^\s*\w+\s+(\w+)\s*\(', line)
        if func_match:
            func_name = func_match.group(1)
            if func_name in line[line.find('('):]:
                risks.append((i, f"Possible recursion: {func_name}", line.strip()))
    
    return risks

if __name__ == '__main__':
    for filepath in sys.argv[1:]:
        risks = scan_for_stack_risks(filepath)
        if risks:
            print(f"\n{'='*60}")
            print(f"FILE: {filepath}")
            print(f"{'='*60}")
            for line_no, reason, code in risks:
                print(f"  Line {line_no}: {reason}")
                print(f"    > {code}")
```

## Mitigation Strategies

### Strategy 1: Increase Stack Size

In STM32CubeMX or startup_stm32g474xx.s:
```asm
Stack_Size      EQU     0x1000  ; Change from 0x400 (1KB) to 0x1000 (4KB)
```

**Warning:** This reduces available heap/data memory. Only use if truly necessary.

### Strategy 2: Function Inlining

```c
// Force small functions inline to eliminate call overhead
static inline uint32_t calculate_checksum(uint8_t *data, uint16_t len) {
    uint32_t sum = 0;
    for (uint16_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return sum;
}
```

**Compiler hints:**
```c
__attribute__((always_inline))  // Force inline
__attribute__((noinline))       // Prevent inline (for profiling)
```

### Strategy 3: Separate Stacks for Interrupts

Some ARM Cortex-M processors support dual stacks:
```c
// In startup code
void SystemInit(void) {
    // Use PSP (Process Stack Pointer) for main
    // Use MSP (Main Stack Pointer) for interrupts
    __set_PSP((uint32_t)&_estack);
    __set_CONTROL(0x02);  // Use PSP, unprivileged
}
```

### Strategy 4: Compiler Optimizations

```c
// In Keil options
#pragma O3  // Maximum optimization (reduces stack frame sizes)

// Or for GCC
__attribute__((optimize("O3")))
void critical_function(void) {
    // This function will be heavily optimized
}
```

## Real-World Bug Case Study

### Bug: Webpage Feature Disappears

**Symptoms:**
- System boots fine
- NTP sync works
- GPS parsing works  
- LED display updates correctly
- Webpage loads initially
- After ~30 minutes, webpage stops responding
- Other features continue working

**Investigation:**
```c
// Suspected function (httpServer.c)
void generate_config_page(void) {
    char page[1536];  // ❌ 1.5KB local array!
    
    sprintf(page, "<html><head><title>Config</title>...</html>");
    // ...50+ more lines of HTML generation
    
    send_http_response(page);
}
```

**Stack usage analysis:**
- `generate_config_page()`: 1536 bytes
- `send_http_response()`: 256 bytes  
- `W5500_SendData()`: 128 bytes
- Interrupt nesting during HTTP: 256 bytes
- **Total: 2176 bytes** (exceeded 2KB stack!)

**Root cause:** Stack overflow corrupted global variables used by web server state machine, specifically the `http_connection_active` flag.

**Fix:**
```c
// Move to static storage
static char http_page_buffer[1536];

void generate_config_page(void) {
    sprintf(http_page_buffer, "<html><head><title>Config</title>...</html>");
    send_http_response(http_page_buffer);
}
```

**Result:** System now stable for 72+ hour tests.

## Prevention Checklist

Before committing code:

- [ ] Run stack usage analysis: `grep -r "\.su$" build/`
- [ ] No local arrays > 64 bytes (move to static/global)
- [ ] No functions with > 5 levels of calls
- [ ] No recursive functions
- [ ] Printf calls have ≤ 5 arguments
- [ ] Critical paths profiled with debugger
- [ ] Stack watermarking enabled in debug builds
- [ ] Long-duration testing (24+ hours)
- [ ] Stress test with all features active simultaneously

## Debugging Workflow

When encountering suspected stack overflow:

1. **Enable stack watermarking** in startup code
2. **Monitor stack usage** periodically via UART/debug log
3. **Compile with `-fstack-usage`** flag
4. **Review all functions** using > 256 bytes
5. **Profile with debugger** during peak load scenarios
6. **Test with reduced stack** (halve size to force failures faster)
7. **Move large arrays** to static/global storage
8. **Flatten call hierarchies** where possible
9. **Re-test for 48+ hours** under maximum load
