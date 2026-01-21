#!/usr/bin/env python3
"""
Stack Overflow Detection Tool for Embedded C Projects
Analyzes source code and build artifacts to detect potential stack issues

Usage:
    python stack_checker.py --source src/
    python stack_checker.py --su-files build/*.su
    python stack_checker.py --all

Author: Embedded Systems Best Practices
Version: 1.0
Date: 2026-01-21
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

# Configuration
MAX_CALL_DEPTH = 7
MAX_LOCAL_ARRAY = 128
MAX_PRINTF_ARGS = 5
STACK_SIZE_THRESHOLD = 256  # Warn if function uses > 256 bytes

class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("  STACK OVERFLOW DETECTION TOOL")
    print("  Embedded C Project Analyzer")
    print("=" * 70)
    print(f"{Colors.END}\n")

def check_large_local_arrays(filepath: str) -> List[Tuple[int, str]]:
    """
    Check for local arrays larger than MAX_LOCAL_ARRAY bytes
    Returns: List of (line_number, description)
    """
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        in_function = False
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            # Track function scope
            if re.match(r'^\w+.*\(.*\)\s*{', line):
                in_function = True
                brace_count = 1
                continue
                
            if in_function:
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0:
                    in_function = False
                    
                # Check for array declarations
                # Match: type name[SIZE] or type name[SIZE][SIZE2]
                array_match = re.search(
                    r'\b(\w+)\s+(\w+)\s*\[(\d+)\](?:\s*\[(\d+)\])?',
                    line
                )
                
                if array_match and in_function:
                    type_name = array_match.group(1)
                    var_name = array_match.group(2)
                    size1 = int(array_match.group(3))
                    size2 = int(array_match.group(4)) if array_match.group(4) else 1
                    
                    # Skip if it's static
                    if 'static' in line:
                        continue
                        
                    # Estimate size (crude, assumes 4 bytes per element)
                    element_size = 1 if 'char' in type_name else 4
                    total_size = size1 * size2 * element_size
                    
                    if total_size > MAX_LOCAL_ARRAY:
                        issues.append((
                            i,
                            f"Local array '{var_name}[{size1}]' = "
                            f"{total_size} bytes (>{MAX_LOCAL_ARRAY})"
                        ))
                        
    except Exception as e:
        print(f"{Colors.RED}Error reading {filepath}: {e}{Colors.END}")
        
    return issues

def check_printf_arguments(filepath: str) -> List[Tuple[int, str]]:
    """
    Check for printf/sprintf/LOG_DEBUG with too many arguments
    Returns: List of (line_number, description)
    """
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Match printf-like functions
        printf_pattern = re.compile(
            r'(printf|sprintf|snprintf|LOG_\w+|fprintf)\s*\([^)]+\)',
            re.MULTILINE
        )
        
        for match in printf_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            matched_text = match.group(0)
            
            # Count commas (rough estimate of argument count)
            # Exclude commas inside strings
            in_string = False
            arg_count = 0
            for char in matched_text:
                if char == '"':
                    in_string = not in_string
                elif char == ',' and not in_string:
                    arg_count += 1
                    
            if arg_count > MAX_PRINTF_ARGS:
                issues.append((
                    line_num,
                    f"{match.group(1)}() has {arg_count} arguments "
                    f"(>{MAX_PRINTF_ARGS})"
                ))
                
    except Exception as e:
        print(f"{Colors.RED}Error reading {filepath}: {e}{Colors.END}")
        
    return issues

def check_recursion(filepath: str) -> List[Tuple[int, str]]:
    """
    Simple heuristic check for potential recursion
    Returns: List of (line_number, description)
    """
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Extract function names
        function_names = set()
        for line in lines:
            func_match = re.match(r'^(\w+)\s+(\w+)\s*\([^)]*\)\s*{', line)
            if func_match:
                function_names.add(func_match.group(2))
                
        # Check if functions call themselves
        current_func = None
        for i, line in enumerate(lines, 1):
            func_match = re.match(r'^(\w+)\s+(\w+)\s*\([^)]*\)\s*{', line)
            if func_match:
                current_func = func_match.group(2)
                
            if current_func:
                # Check if current function calls itself
                if re.search(rf'\b{current_func}\s*\(', line):
                    if not re.match(r'^\s*//', line):  # Skip comments
                        issues.append((
                            i,
                            f"Potential recursion in '{current_func}()'"
                        ))
                        
    except Exception as e:
        print(f"{Colors.RED}Error reading {filepath}: {e}{Colors.END}")
        
    return issues

def analyze_su_files(su_files: List[str]) -> Dict[str, int]:
    """
    Analyze .su files generated by -fstack-usage
    Returns: Dict of {function_name: stack_usage}
    """
    stack_usage = {}
    
    for su_file in su_files:
        try:
            with open(su_file, 'r') as f:
                for line in f:
                    # Format: filename:line:column:function_name	size	type
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        func_info = parts[0].split(':')
                        if len(func_info) >= 4:
                            func_name = func_info[3]
                            size = int(parts[1])
                            stack_usage[func_name] = size
        except Exception as e:
            print(f"{Colors.RED}Error reading {su_file}: {e}{Colors.END}")
            
    return stack_usage

def analyze_source_files(directory: str):
    """Main analysis function for source files"""
    print(f"{Colors.BOLD}Analyzing source files in: {directory}{Colors.END}\n")
    
    total_issues = 0
    files_checked = 0
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(('.c', '.cpp', '.cc')):
                filepath = os.path.join(root, filename)
                files_checked += 1
                
                file_issues = 0
                
                # Check large local arrays
                array_issues = check_large_local_arrays(filepath)
                if array_issues:
                    print(f"\n{Colors.YELLOW}⚠️  {filepath}{Colors.END}")
                    print(f"{Colors.BOLD}Large Local Arrays:{Colors.END}")
                    for line_num, desc in array_issues:
                        print(f"  Line {line_num}: {desc}")
                        file_issues += 1
                        
                # Check printf arguments
                printf_issues = check_printf_arguments(filepath)
                if printf_issues:
                    if file_issues == 0:
                        print(f"\n{Colors.YELLOW}⚠️  {filepath}{Colors.END}")
                    print(f"{Colors.BOLD}Too Many Printf Arguments:{Colors.END}")
                    for line_num, desc in printf_issues:
                        print(f"  Line {line_num}: {desc}")
                        file_issues += 1
                        
                # Check recursion
                recursion_issues = check_recursion(filepath)
                if recursion_issues:
                    if file_issues == 0:
                        print(f"\n{Colors.RED}🚨 {filepath}{Colors.END}")
                    print(f"{Colors.BOLD}{Colors.RED}Potential Recursion:{Colors.END}")
                    for line_num, desc in recursion_issues:
                        print(f"  Line {line_num}: {desc}")
                        file_issues += 1
                        
                total_issues += file_issues
                
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print(f"  Files checked: {files_checked}")
    print(f"  Total issues:  {total_issues}")
    
    if total_issues == 0:
        print(f"\n{Colors.GREEN}✅ No stack overflow risks detected!{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}⚠️  {total_issues} potential issues found!{Colors.END}\n")
        
    return total_issues

def analyze_stack_usage(su_files: List[str]):
    """Analyze stack usage from .su files"""
    print(f"{Colors.BOLD}Analyzing stack usage files{Colors.END}\n")
    
    if not su_files:
        print(f"{Colors.RED}No .su files found!{Colors.END}")
        print("Build with: -fstack-usage flag")
        return
        
    stack_usage = analyze_su_files(su_files)
    
    if not stack_usage:
        print(f"{Colors.RED}No stack usage data found{Colors.END}\n")
        return
        
    # Sort by stack usage
    sorted_usage = sorted(stack_usage.items(), key=lambda x: x[1], reverse=True)
    
    print(f"{Colors.BOLD}Top 20 Stack Consumers:{Colors.END}\n")
    print(f"{'Function':<40} {'Stack (bytes)':<15} {'Status'}")
    print("-" * 70)
    
    for func, size in sorted_usage[:20]:
        if size > STACK_SIZE_THRESHOLD:
            status = f"{Colors.RED}⚠️  HIGH{Colors.END}"
        elif size > STACK_SIZE_THRESHOLD // 2:
            status = f"{Colors.YELLOW}⚠️  MEDIUM{Colors.END}"
        else:
            status = f"{Colors.GREEN}✅ OK{Colors.END}"
            
        print(f"{func:<40} {size:<15} {status}")
        
    total_stack = sum(stack_usage.values())
    print(f"\n{Colors.BOLD}Total stack usage (sum of all functions): {total_stack} bytes{Colors.END}")
    print(f"Note: Actual usage depends on call chain depth\n")

def main():
    parser = argparse.ArgumentParser(
        description='Stack Overflow Detection Tool for Embedded C'
    )
    parser.add_argument(
        '--source', '-s',
        help='Source directory to analyze',
        default='.'
    )
    parser.add_argument(
        '--su-files', '-u',
        help='Pattern for .su files (e.g., "build/*.su")',
        default=None
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all checks'
    )
    
    args = parser.parse_args()
    
    print_header()
    
    # Source code analysis
    if args.all or (not args.su_files):
        issues = analyze_source_files(args.source)
    
    # Stack usage analysis
    if args.su_files or args.all:
        su_files = []
        if args.su_files:
            import glob
            su_files = glob.glob(args.su_files)
        else:
            # Search for .su files
            for root, dirs, files in os.walk('.'):
                for f in files:
                    if f.endswith('.su'):
                        su_files.append(os.path.join(root, f))
                        
        if su_files:
            analyze_stack_usage(su_files)
    
    print(f"{Colors.BOLD}Recommendations:{Colors.END}")
    print("  1. Review all flagged issues")
    print("  2. Refactor functions with large local arrays")
    print("  3. Reduce printf/LOG_DEBUG arguments")
    print("  4. Flatten call chains where possible")
    print("  5. Add stack monitoring to production code")
    print("\nFor more info, see: STACK_OVERFLOW_PREVENTION_STANDARD_EN.md\n")

if __name__ == '__main__':
    main()
