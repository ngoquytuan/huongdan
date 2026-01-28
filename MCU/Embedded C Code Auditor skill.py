#!/usr/bin/env python3
"""
Embedded C Code Auditor
Scans C source files for common embedded systems vulnerabilities
"""

import re
import sys
import os
from collections import defaultdict

class EmbeddedCodeAuditor:
    def __init__(self):
        self.findings = defaultdict(list)
        
    def scan_file(self, filepath):
        """Scan a single C file for vulnerabilities"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return
        
        # Run all checks
        self.check_volatile_keywords(lines, filepath)
        self.check_exact_comparisons(lines, filepath)
        self.check_large_arrays(lines, filepath)
        self.check_printf_args(lines, filepath)
        self.check_blocking_in_isr(lines, filepath)
        self.check_string_operations(lines, filepath)
        self.check_buffer_operations(lines, filepath)
        self.check_recursion(lines, filepath)
        
    def check_volatile_keywords(self, lines, filepath):
        """Check for missing volatile on shared variables"""
        # Look for potential shared variables (accessed in ISR context)
        in_isr = False
        isr_variables = set()
        
        for i, line in enumerate(lines, 1):
            # Detect ISR handlers
            if re.search(r'IRQHandler|Callback|ISR', line):
                in_isr = True
            
            # Track variable usage in ISR
            if in_isr:
                # Find variable assignments
                matches = re.findall(r'\b(\w+)\s*=', line)
                isr_variables.update(matches)
                
                # End of function
                if line.strip().startswith('}') and in_isr:
                    in_isr = False
        
        # Check if these variables have volatile declaration
        for i, line in enumerate(lines, 1):
            for var in isr_variables:
                # Look for variable declaration
                pattern = rf'\b(uint\w+|int\w+|char)\s+{var}\s*[;=\[]'
                if re.search(pattern, line) and 'volatile' not in line:
                    self.findings['missing_volatile'].append({
                        'file': filepath,
                        'line': i,
                        'code': line.strip(),
                        'reason': f'Variable "{var}" used in ISR but not declared volatile'
                    })
    
    def check_exact_comparisons(self, lines, filepath):
        """Check for exact == comparisons with interrupt counters"""
        counter_patterns = [
            r'\b(counter|count|tick|pps|timer)\w*\s*==',
            r'==\s*\b(counter|count|tick|pps|timer)',
            r'TIM\d+->CNT\s*==',
            r'==\s*TIM\d+->CNT'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in counter_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Exclude comments
                    if not line.strip().startswith('//'):
                        self.findings['exact_comparison'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip(),
                            'reason': 'Exact comparison with counter (use >= instead)'
                        })
    
    def check_large_arrays(self, lines, filepath):
        """Check for large local arrays on stack"""
        for i, line in enumerate(lines, 1):
            # Match local array declarations
            match = re.search(r'(char|uint8_t|int|uint32_t)\s+\w+\[(\d+)\]', line)
            if match:
                size = int(match.group(2))
                if size > 64:
                    # Check if it's static
                    if 'static' not in line:
                        self.findings['large_array'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip(),
                            'reason': f'Large array [{size} bytes] on stack (consider static)'
                        })
    
    def check_printf_args(self, lines, filepath):
        """Check for printf/sprintf with many arguments"""
        for i, line in enumerate(lines, 1):
            if 'printf' in line or 'sprintf' in line:
                # Count format specifiers
                percent_count = line.count('%') - line.count('%%')
                if percent_count > 5:
                    self.findings['printf_args'].append({
                        'file': filepath,
                        'line': i,
                        'code': line.strip()[:80] + '...',
                        'reason': f'Printf with {percent_count} arguments (stack overflow risk)'
                    })
    
    def check_blocking_in_isr(self, lines, filepath):
        """Check for blocking operations in ISR handlers"""
        in_isr = False
        isr_start = 0
        
        for i, line in enumerate(lines, 1):
            # Detect ISR start
            if re.search(r'IRQHandler|Callback', line) and '{' in line:
                in_isr = True
                isr_start = i
            
            if in_isr:
                # Check for blocking operations
                blocking_ops = [
                    (r'HAL_I2C_(Mem_)?Transmit|HAL_I2C_(Mem_)?Receive', 'I2C blocking operation'),
                    (r'HAL_SPI_Transmit|HAL_SPI_Receive', 'SPI blocking operation'),
                    (r'HAL_UART_Transmit|HAL_UART_Receive', 'UART blocking operation'),
                    (r'\bprintf\b|\bsprintf\b', 'Printf in ISR'),
                    (r'HAL_Delay', 'HAL_Delay in ISR'),
                    (r'\bmalloc\b|\bfree\b', 'Heap allocation in ISR')
                ]
                
                for pattern, reason in blocking_ops:
                    if re.search(pattern, line):
                        self.findings['blocking_in_isr'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip(),
                            'reason': f'{reason} (ISR started at line {isr_start})'
                        })
                
                # End of ISR
                if line.strip() == '}':
                    in_isr = False
    
    def check_string_operations(self, lines, filepath):
        """Check for unsafe string operations"""
        unsafe_patterns = [
            (r'\bstrcpy\s*\(', 'strcpy (use strncpy instead)'),
            (r'\bstrcat\s*\(', 'strcat (use strncat instead)'),
            (r'\bsprintf\s*\(', 'sprintf (use snprintf instead)'),
            (r'\bgets\s*\(', 'gets (unsafe, use fgets instead)')
        ]
        
        for i, line in enumerate(lines, 1):
            if not line.strip().startswith('//'):  # Skip comments
                for pattern, reason in unsafe_patterns:
                    if re.search(pattern, line):
                        self.findings['unsafe_string'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip(),
                            'reason': reason
                        })
    
    def check_buffer_operations(self, lines, filepath):
        """Check for buffer operations without bounds checking"""
        for i, line in enumerate(lines, 1):
            # Array index without bounds check
            if re.search(r'\w+\[\w+\+\+\]', line):
                # Check if there's a bounds check nearby
                context = ''.join(lines[max(0, i-3):i])
                if 'if' not in context and 'sizeof' not in context:
                    self.findings['missing_bounds_check'].append({
                        'file': filepath,
                        'line': i,
                        'code': line.strip(),
                        'reason': 'Array index increment without visible bounds check'
                    })
    
    def check_recursion(self, lines, filepath):
        """Check for recursive function calls"""
        functions = {}
        current_func = None
        
        # First pass: identify functions
        for i, line in enumerate(lines, 1):
            match = re.search(r'^\s*\w+\s+(\w+)\s*\([^)]*\)\s*{', line)
            if match:
                current_func = match.group(1)
                functions[current_func] = i
        
        # Second pass: check for recursion
        current_func = None
        for i, line in enumerate(lines, 1):
            match = re.search(r'^\s*\w+\s+(\w+)\s*\([^)]*\)\s*{', line)
            if match:
                current_func = match.group(1)
            
            if current_func:
                # Check if function calls itself
                if re.search(rf'\b{current_func}\s*\(', line):
                    # Make sure it's not the function definition
                    if not re.match(r'^\s*\w+\s+', line):
                        self.findings['recursion'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip(),
                            'reason': f'Possible recursion in function "{current_func}"'
                        })
    
    def print_report(self):
        """Print audit report"""
        print("\n" + "="*80)
        print("EMBEDDED C CODE AUDIT REPORT")
        print("="*80 + "\n")
        
        categories = {
            'exact_comparison': ('⚠️  EXACT COMPARISONS WITH COUNTERS', 'HIGH'),
            'missing_volatile': ('⚠️  MISSING VOLATILE KEYWORDS', 'HIGH'),
            'blocking_in_isr': ('⚠️  BLOCKING OPERATIONS IN ISR', 'CRITICAL'),
            'large_array': ('⚠️  LARGE ARRAYS ON STACK', 'MEDIUM'),
            'printf_args': ('⚠️  PRINTF WITH MANY ARGUMENTS', 'MEDIUM'),
            'unsafe_string': ('⚠️  UNSAFE STRING OPERATIONS', 'MEDIUM'),
            'missing_bounds_check': ('⚠️  MISSING BOUNDS CHECKS', 'MEDIUM'),
            'recursion': ('⚠️  RECURSIVE FUNCTIONS', 'HIGH')
        }
        
        total_issues = sum(len(findings) for findings in self.findings.values())
        
        if total_issues == 0:
            print("✅ No issues found! Code looks clean.\n")
            return
        
        print(f"Found {total_issues} potential issues:\n")
        
        for category, findings in self.findings.items():
            if not findings:
                continue
            
            title, severity = categories.get(category, (category.upper(), 'UNKNOWN'))
            print(f"\n{title} [{severity}] - {len(findings)} issues")
            print("-" * 80)
            
            for finding in findings:
                print(f"\n  File: {finding['file']}")
                print(f"  Line: {finding['line']}")
                print(f"  Code: {finding['code']}")
                print(f"  Issue: {finding['reason']}")
        
        print("\n" + "="*80)
        print(f"SUMMARY: {total_issues} issues found")
        print("="*80 + "\n")
        
        # Priority recommendations
        print("PRIORITY FIXES:")
        if self.findings['blocking_in_isr']:
            print("  1. 🔴 Remove blocking operations from ISR handlers")
        if self.findings['missing_volatile']:
            print("  2. 🔴 Add volatile to ISR-shared variables")
        if self.findings['exact_comparison']:
            print("  3. 🔴 Change exact comparisons to range checks (>=)")
        if self.findings['recursion']:
            print("  4. 🔴 Eliminate recursive functions")
        if self.findings['large_array']:
            print("  5. 🟡 Move large arrays to static/global storage")
        if self.findings['printf_args']:
            print("  6. 🟡 Split printf calls with many arguments")
        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 audit_embedded_c.py <file_or_directory>")
        print("\nScans C source files for common embedded systems vulnerabilities:")
        print("  - Race conditions (missing volatile, exact comparisons)")
        print("  - Stack overflow (large arrays, many printf args)")
        print("  - Blocking operations in ISRs")
        print("  - Unsafe string operations")
        print("  - Missing bounds checks")
        print("  - Recursive functions")
        sys.exit(1)
    
    path = sys.argv[1]
    auditor = EmbeddedCodeAuditor()
    
    # Scan files
    if os.path.isfile(path):
        if path.endswith(('.c', '.h')):
            print(f"Scanning file: {path}")
            auditor.scan_file(path)
    elif os.path.isdir(path):
        print(f"Scanning directory: {path}")
        for root, dirs, files in os.walk(path):
            # Skip build directories
            dirs[:] = [d for d in dirs if d not in ['build', 'Build', 'Debug', 'Release']]
            
            for file in files:
                if file.endswith(('.c', '.h')):
                    filepath = os.path.join(root, file)
                    auditor.scan_file(filepath)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
    
    # Print report
    auditor.print_report()

if __name__ == '__main__':
    main()
