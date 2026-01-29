# Stack Optimization Report Templates

Complete templates for structured stack analysis reports, derived from production methodology.

## Executive Summary Template

```markdown
# Stack Optimization Analysis Report

**Project**: [Project Name]
**MCU**: STM32G474 (128KB RAM, 512KB Flash)
**Current Stack**: [Size] bytes
**Analysis Date**: [Date]
**Analyst**: [Name]

## Summary

**Total Functions Analyzed**: X
**Inline Candidates Found**:
- 🔴 HIGH Priority: X functions (must inline immediately)
- 🟡 MEDIUM Priority: X functions (should inline this sprint)
- 🟢 LOW Priority: X functions (consider for next sprint)

**Potential Stack Savings**: XXX bytes (YY% reduction)

**Current Status**:
- Max Call Depth: X levels
- Stack Usage (measured): XXX / YYY bytes (ZZ%)
- Critical Paths: [List GPS, NTP, Display, etc.]

**Recommendations**:
1. [Top recommendation]
2. [Second recommendation]
3. [Third recommendation]
```

---

## Function Analysis Template

### Complete Format (from proven methodology)

```markdown
## 🎯 Function: `function_name()`

**📍 Location**: `filename.c:line_number`

**📊 Metrics**:
- Current Call Depth: X levels
- Function Size: Y lines of code
- Local Variables: Z bytes
- Called From: N locations
- Stack Frame Cost: ~32 bytes

**🔗 Current Call Chain**:
\```
main() 
  → system_main_loop()      [Level 1: +32B]
    → slaveClockRun()       [Level 2: +32B]
      → oneSecondfucns()    [Level 3: +32B]
        → gps_once()        [Level 4: +32B]
          → THIS_FUNCTION() [Level 5: +32B]

TOTAL OVERHEAD: XXX bytes
\```

**💾 Stack Impact**:
- Current stack usage: X bytes (call chain overhead)
- After inline: Y bytes
- **SAVINGS: Z bytes (P% reduction)**

**🎚️ Priority**: 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW

**✅ Recommendation**: INLINE / KEEP SEPARATE

**📝 Rationale**:
1. [Reason 1 based on criteria]
2. [Reason 2 with data]
3. [Reason 3 with impact]

**🔧 Implementation**:

**BEFORE** (Current Code):
\```c
void parent_function(void) {
    // ... code ...
    result = child_function(param1, param2);
    // ... code ...
}

int child_function(int a, int b) {
    int local_var = a + b;
    return local_var * 2;
}
\```

**AFTER** (Inlined Code):
\```c
void parent_function(void) {
    // ... code ...
    
    // ✅ INLINED: child_function()
    {
        int local_var = param1 + param2;
        result = local_var * 2;
    }
    
    // ... code ...
}

// ❌ REMOVED: child_function()
\```

**⚠️ Risk Assessment**:
- Code duplication: None / Low / High
- Maintainability: Good / Acceptable / Poor
- Testing required: Minimal / Moderate / Extensive

**🔍 Testing Plan**:
1. [Test step 1]
2. [Test step 2]
3. [Verification criteria]

---
```

### Condensed Format (for summary tables)

```markdown
| Function | File:Line | Depth | Size | Calls | Locals | Savings | Priority |
|----------|-----------|-------|------|-------|--------|---------|----------|
| func1()  | gps.c:234 | 7     | 12   | 1     | 8B     | 192B    | HIGH     |
| func2()  | main.c:89 | 6     | 18   | 2     | 16B    | 128B    | MEDIUM   |
| func3()  | disp.c:45 | 5     | 25   | 3     | 32B    | 96B     | LOW      |
```

---

## Call Depth Analysis Template

### Visual Call Graph (ASCII)

```markdown
## Call Depth Analysis

### Critical Path 1: GPS Timing Chain

\```
main()                          [Depth 0]  Stack: 128B
  │
  └─> system_main_loop()        [Depth 1]  +32B = 160B
        │
        └─> slaveClockRun()     [Depth 2]  +32B = 192B
              │
              └─> oneSecondfucns() [D 3]   +32B = 224B
                    │
                    ├─> gps_once()  [D 4]  +32B = 256B
                    │     │
                    │     └─> stable_frac_offset() [D 5] +32B = 288B
                    │           │
                    │           └─> LOG_DEBUG() [D 6] +256B = 544B ⚠️
                    │
                    └─> ntp_client()  [D 4]  +128B = 352B
                          │
                          └─> process_packet() [D 5] +64B = 416B

MAX DEPTH: 6 levels
PEAK USAGE: 544 bytes (GPS path with logging)
\```

### Critical Path 2: Display Update

\```
main()
  └─> system_main_loop()
        └─> slaveClockRun()
              └─> display_update()  [D 3]  +64B
                    └─> format_time()  [D 4]  +128B
                          └─> sprintf()  [D 5]  +256B

MAX DEPTH: 5 levels
PEAK USAGE: 480 bytes
\```

### Summary

| Path | Max Depth | Peak Usage | Bottleneck |
|------|-----------|------------|------------|
| GPS  | 6 levels  | 544 bytes  | LOG_DEBUG  |
| NTP  | 5 levels  | 416 bytes  | process_packet |
| Display | 5 levels | 480 bytes | sprintf |
| Network | 4 levels | 320 bytes | W5500_SendData |
```

---

## Implementation Roadmap Template

```markdown
## Implementation Roadmap

### Phase 1: CRITICAL (Immediate - This Week)

**Goal**: Reduce stack by 200+ bytes to prevent crashes

| Priority | Function | File | Savings | Risk | Effort |
|----------|----------|------|---------|------|--------|
| 🔴 1 | stable_frac_offset() | gps.c:245 | 192B | Low | 2h |
| 🔴 2 | get_time_components() | time.c:89 | 128B | Low | 1h |
| 🔴 3 | validate_gps_data() | gps.c:567 | 96B | Low | 1h |

**Total Savings**: 416 bytes (20% reduction)
**Timeline**: 3 days
**Testing**: Full system test after each inline

### Phase 2: IMPORTANT (This Sprint - 2 Weeks)

**Goal**: Further optimize to <70% usage

| Priority | Function | File | Savings | Risk | Effort |
|----------|----------|------|---------|------|--------|
| 🟡 4 | format_display_buffer() | display.c:123 | 128B | Medium | 3h |
| 🟡 5 | parse_ntp_response() | ntp.c:234 | 96B | Medium | 2h |
| 🟡 6 | update_led_matrix() | display.c:456 | 64B | Low | 2h |

**Total Savings**: 288 bytes (14% reduction)
**Timeline**: 1 week
**Testing**: Stress test with all features

### Phase 3: OPTIONAL (Next Sprint)

**Goal**: Polish and fine-tune

| Priority | Function | File | Savings | Risk | Effort |
|----------|----------|------|---------|------|--------|
| 🟢 7 | helper_function_a() | utils.c:89 | 64B | Low | 1h |
| 🟢 8 | helper_function_b() | utils.c:123 | 64B | Low | 1h |

**Total Savings**: 128 bytes (6% reduction)

---

### Cumulative Impact

| Phase | Savings | Cumulative | Usage After | Status |
|-------|---------|------------|-------------|--------|
| Baseline | - | - | 1800/2048 (88%) | ⚠️ Critical |
| Phase 1 | 416B | 416B | 1384/2048 (68%) | ✅ Safe |
| Phase 2 | 288B | 704B | 1096/2048 (54%) | ✅ Good |
| Phase 3 | 128B | 832B | 968/2048 (47%) | ✅ Excellent |

**Target**: <70% usage (1433 bytes)
**Achieved After Phase 1**: ✅ YES
```

---

## Risk Assessment Template

```markdown
## Risk Assessment

### Overall Risk Level: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH

### Potential Issues

**1. Code Duplication**
- **Risk**: Functions called multiple times create code bloat
- **Impact**: Flash usage +5-10%
- **Mitigation**: Only inline functions called <3 times
- **Status**: ✅ Mitigated

**2. Maintainability**
- **Risk**: Inlined code harder to debug
- **Impact**: Development time +10%
- **Mitigation**: Add inline comments, preserve function names in comments
- **Status**: ⚠️ Monitor

**3. Timing Changes**
- **Risk**: Inline may affect GPS/NTP sub-millisecond timing
- **Impact**: Accuracy degradation
- **Mitigation**: Measure PPS jitter before/after
- **Status**: ✅ Test plan ready

### Testing Recommendations

**Before Optimization**:
1. ✅ Measure baseline stack (watermark)
2. ✅ Record GPS timing accuracy (PPS jitter)
3. ✅ Capture NTP sync stability
4. ✅ Document display update rate

**After Each Inline**:
1. ✅ Re-measure stack usage
2. ✅ Verify functionality (bit-identical output)
3. ✅ Check timing (GPS PPS < 1ms jitter)
4. ✅ Run 24-hour stress test

**Final Validation**:
1. ✅ Stack usage <70% (measured)
2. ✅ No functional regressions
3. ✅ Timing within spec (GPS ±1ms, NTP ±10ms)
4. ✅ Code size increase <5%
5. ✅ 48-hour burn-in test

### Rollback Strategy

**If issues occur**:
1. Revert last inline (Git rollback)
2. Re-test with previous version
3. Document failure mode
4. Re-analyze with updated criteria

**Rollback triggers**:
- Stack usage not reduced
- Functional regression detected
- Timing accuracy degraded
- Build size increased >10%
```

---

## Summary Table Template

```markdown
## Summary Table: Top 10 Inline Candidates

| # | Function | Location | Depth | Size | Calls | Locals | Savings | Priority | Status |
|---|----------|----------|-------|------|-------|--------|---------|----------|--------|
| 1 | stable_frac_offset() | gps.c:245 | 7 | 12 | 1 | 8B | 192B | 🔴 HIGH | ⏳ Pending |
| 2 | get_time_components() | time.c:89 | 6 | 18 | 2 | 16B | 128B | 🔴 HIGH | ⏳ Pending |
| 3 | validate_gps_data() | gps.c:567 | 6 | 15 | 1 | 12B | 96B | 🔴 HIGH | ⏳ Pending |
| 4 | format_display_buffer() | display.c:123 | 5 | 22 | 2 | 32B | 128B | 🟡 MEDIUM | ⏳ Pending |
| 5 | parse_ntp_response() | ntp.c:234 | 5 | 24 | 1 | 24B | 96B | 🟡 MEDIUM | ⏳ Pending |
| 6 | update_led_matrix() | display.c:456 | 5 | 20 | 3 | 16B | 64B | 🟡 MEDIUM | ⏳ Pending |
| 7 | calculate_checksum() | utils.c:89 | 4 | 10 | 4 | 4B | 64B | 🟢 LOW | ⏳ Pending |
| 8 | helper_function_a() | utils.c:123 | 4 | 15 | 3 | 8B | 64B | 🟢 LOW | ⏳ Pending |
| 9 | clamp_value() | math.c:45 | 3 | 8 | 5 | 0B | 32B | 🟢 LOW | ⏳ Pending |
| 10 | min_max() | math.c:67 | 3 | 6 | 6 | 0B | 32B | 🟢 LOW | ⏳ Pending |

**Total Potential Savings**: 896 bytes (44% reduction)
**Target Achieved**: ✅ YES (>200 bytes)
```

---

## Example: Complete Function Analysis

### Real-World Example from GPS Clock Project

```markdown
## 🎯 Function: `stable_frac_offset()`

**📍 Location**: `gps.c:245`

**📊 Metrics**:
- Current Call Depth: 7 levels
- Function Size: 12 lines of code
- Local Variables: 4 bytes (single uint32_t)
- Called From: 1 location (gps_once() only)
- Stack Frame Cost: ~32 bytes

**🔗 Current Call Chain**:
\```
main() 
  → system_main_loop()      [Level 1: +32B]
    → slaveClockRun()       [Level 2: +32B]
      → oneSecondfucns()    [Level 3: +32B]
        → gps_once()        [Level 4: +32B]
          → stable_frac_offset() [Level 5: +32B]
            → LOG_DEBUG()   [Level 6: +256B vsnprintf]

TOTAL OVERHEAD: 416 bytes
\```

**💾 Stack Impact**:
- Current: 416 bytes overhead (call chain)
- After inline into gps_once(): 224 bytes overhead
- **SAVINGS: 192 bytes (46% reduction)**

**🎚️ Priority**: 🔴 HIGH

**✅ Recommendation**: INLINE into oneSecondfucns() or gps_once()

**📝 Rationale**:
1. **Very deep call chain** (7 levels) - major stack pressure
2. **Small function** (12 lines) - perfect inline candidate
3. **Called only once** - zero code duplication
4. **Critical GPS timing path** - inline improves performance
5. **High stack savings** (192 bytes = 9.4% of total 2KB stack!)

**🔧 Implementation**:

**BEFORE** (Current Code):
\```c
void gps_once(void) {
    // ... GPS parsing logic ...
    
    uint32_t offset = stable_frac_offset(gps_data.fraction);
    
    // ... use offset ...
}

static uint32_t stable_frac_offset(uint32_t raw_frac) {
    uint32_t stable = raw_frac;
    
    // Apply filtering
    if (raw_frac < 100 || raw_frac > 9900) {
        stable = 0;  // Reset if jitter too high
    }
    
    LOG_DEBUG("[GPS] Frac offset: %lu", stable);
    return stable;
}
\```

**AFTER** (Inlined Code):
\```c
void gps_once(void) {
    // ... GPS parsing logic ...
    
    // ✅ INLINED: stable_frac_offset()
    uint32_t offset;
    {
        uint32_t raw_frac = gps_data.fraction;
        offset = raw_frac;
        
        // Apply filtering
        if (raw_frac < 100 || raw_frac > 9900) {
            offset = 0;  // Reset if jitter too high
        }
        
        LOG_DEBUG("[GPS] Frac offset: %lu", offset);
    }
    
    // ... use offset ...
}

// ❌ REMOVED: stable_frac_offset() - no longer needed
\```

**⚠️ Risk Assessment**:
- Code duplication: **None** (called only once)
- Maintainability: **Good** (logic stays together, added comment)
- Testing required: **Minimal** (preserve exact behavior, verify GPS accuracy)

**🔍 Testing Plan**:
1. Measure stack before: ~1800 bytes
2. Apply inline
3. Measure stack after: expect ~1600 bytes
4. Verify GPS PPS jitter unchanged (<1ms)
5. Run 24-hour test, monitor for crashes

---
```

## Usage Guidelines

### When to Use Each Template

**Executive Summary**: Start of every analysis report  
**Function Analysis**: For each inline candidate (top 10 minimum)  
**Call Depth Analysis**: After building call graph  
**Implementation Roadmap**: After prioritizing all candidates  
**Risk Assessment**: Before starting implementation  
**Summary Table**: As quick reference in report

### Customization

Replace placeholders:
- `[Project Name]` → Your project name
- `XXX` → Actual measurements
- `[Date]` → Analysis date
- File:line → Actual source locations

### Automation

Use scripts to auto-generate:
- Summary tables from analysis data
- Call graphs from source parsing
- Stack calculations from GCC .su files