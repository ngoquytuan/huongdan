# Call Depth Analysis Methodology

## Building Call Graphs

### Manual Method

**Step 1**: Start from main()
```c
void main(void) {
    HAL_Init();           // Depth 1
    while(1) {
        system_loop();    // Depth 1
    }
}
```

**Step 2**: Trace each function call
```c
void system_loop(void) {    // Depth 1
    clock_run();            // Depth 2
}

void clock_run(void) {      // Depth 2
    one_second_tasks();     // Depth 3
}

void one_second_tasks(void) { // Depth 3
    gps_process();            // Depth 4
}
```

**Step 3**: Mark maximum depth per path

### Automated Method

**Using cscope**:
```bash
cscope -b -R  # Build database
cscope -d    # Query
# Then: Find functions called by main
```

**Using ctags**:
```bash
ctags -R .
grep "^main" tags  # Find main definition
# Manually trace calls
```

**Using Python script**:
```bash
python3 scripts/analyze_call_depth.py /path/to/src
```

## Identifying Critical Paths

**GPS Timing**: main → ... → gps_once → stable_frac  
**NTP Sync**: main → ... → ntp_client → process_packet  
**Display**: main → ... → display_update → format_time

Focus optimization on deepest paths (>6 levels).

## Calculating Stack Overhead

**Formula**:
```
Total = Σ(Frame_Overhead + Local_Variables)
Frame_Overhead ≈ 32 bytes (ARM Cortex-M)
```

**Example**:
```
main()              32B + 64B locals = 96B
  system_loop()     32B + 16B locals = 48B
    clock_run()     32B + 0B locals  = 32B
      gps_process() 32B + 128B locals = 160B

Total: 96 + 48 + 32 + 160 = 336 bytes
```

## Visual Representations

### ASCII Tree
```
main() [D0: 128B]
  ├─> system_loop() [D1: +32B = 160B]
  │     └─> clock_run() [D2: +32B = 192B]
  │           └─> gps_process() [D3: +128B = 320B]
  │
  └─> display_update() [D1: +64B = 192B]
```

### Depth Histogram
```
Depth | Functions | Max Stack
------|-----------|----------
  1   |    5      |  160B
  2   |   12      |  224B
  3   |   18      |  320B
  4   |   15      |  416B
  5   |    8      |  544B ← Critical
  6   |    3      |  608B ← Critical
  7   |    1      |  704B ← Critical
```

## Optimization Strategy

1. Target depth > 6 first
2. Look for small functions (<15 lines)
3. Inline from deepest to shallowest
4. Re-measure after each change