# Inline Strategies & Decision Criteria

## Priority Classification

### 🔴 HIGH PRIORITY (Must Inline)

**Criteria**:
- Call depth > 6 levels
- Function size < 15 lines
- Called 1-2 places
- Local vars < 32 bytes
- Critical timing path

**Stack savings**: Usually 128-256 bytes per function

**Example**:
```c
// 7 levels deep, 12 lines, called once
static uint32_t stable_frac_offset(uint32_t raw) {
    if (raw < 100 || raw > 9900) return 0;
    return raw;
}
// → INLINE immediately, saves 192 bytes
```

### 🟡 MEDIUM PRIORITY (Should Inline)

**Criteria**:
- Call depth = 5-6 levels
- Function size < 25 lines
- Called 2-3 places
- Local vars < 64 bytes

**Stack savings**: 64-128 bytes

### 🟢 LOW PRIORITY (Consider)

**Criteria**:
- Call depth = 4-5 levels
- Function size < 30 lines
- Called 3-4 places

**Stack savings**: 32-64 bytes

### ❌ NEVER INLINE

**Criteria**:
- Function > 30 lines (code bloat)
- Called > 4 places (excessive duplication)
- Large buffers (>128 bytes local)
- Recursive
- Needs debugging isolation

## GCC Attributes

### Force Inline
```c
static inline __attribute__((always_inline))
int must_inline(int x) {
    return x * 2;
}
```

### Prevent Inline
```c
__attribute__((noinline))
void keep_separate(void) {
    // Debug/profile
}
```

### Flatten (Inline All Callees)
```c
__attribute__((flatten))
void inline_everything_below(void) {
    helper1();
    helper2();
}
```

## Tradeoffs

### Code Size vs Stack

**Inline once**: +10 bytes code, -32 bytes stack ✅  
**Inline 3x**: +30 bytes code, -96 bytes stack ✅  
**Inline 10x**: +100 bytes code, -320 bytes stack ⚠️

**Threshold**: Inline if called < 4 times

### Maintainability

**Good inline**:
- Small, focused function
- Clear inline comment
- Original function name in comment

**Bad inline**:
- Complex logic scattered
- No documentation
- Multiple levels deep

## Common Patterns

### Pattern 1: Utility Functions

```c
// Before: Helper called everywhere
int clamp(int val, int min, int max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

// After: Make inline
static inline int clamp(int val, int min, int max) {
    return (val < min) ? min : (val > max) ? max : val;
}
```

### Pattern 2: Getter/Setter

```c
// Before
uint32_t get_timestamp(void) { return rtc_time.timestamp; }
void set_timestamp(uint32_t t) { rtc_time.timestamp = t; }

// After: Inline
#define get_timestamp() (rtc_time.timestamp)
#define set_timestamp(t) (rtc_time.timestamp = (t))
```

### Pattern 3: Deep Chain Collapse

```c
// Before: 3-level chain
void A(void) { B(); }
void B(void) { C(); }
void C(void) { /* work */ }

// After: Collapse B and C into A
void A(void) {
    // INLINED: B() → C()
    { /* C work */ }
}
```

## Decision Tree

```
Is function < 30 lines?
  ├─ NO → Keep separate ❌
  └─ YES ─> Is call depth > 6?
             ├─ YES → HIGH priority ✅
             └─ NO ──> Called < 3 times?
                        ├─ YES → MEDIUM priority
                        └─ NO ──> Consider tradeoff
```

## Testing After Inline

1. ✅ Stack reduced (measure)
2. ✅ Functionality identical
3. ✅ No timing regression
4. ✅ Code size acceptable