#!/usr/bin/env python3
"""
STM32 Call Depth Analyzer & Stack Optimizer
Analyzes C source code to identify inline candidates and calculate stack savings
"""

import re
import os
import sys
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

class FunctionInfo:
    def __init__(self, name: str, file: str, line: int):
        self.name = name
        self.file = file
        self.line = line
        self.calls_to: Set[str] = set()
        self.called_from: Set[str] = set()
        self.line_count = 0
        self.local_vars_size = 0
        self.max_depth = 0
        
    def __repr__(self):
        return f"Function({self.name}, depth={self.max_depth}, lines={self.line_count})"

class CallGraphAnalyzer:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.functions: Dict[str, FunctionInfo] = {}
        self.call_chains: List[List[str]] = []
        
    def scan_sources(self):
        """Scan all C files in directory"""
        print(f"🔍 Scanning {self.source_dir}...")
        
        for root, dirs, files in os.walk(self.source_dir):
            # Skip build directories
            dirs[:] = [d for d in dirs if d not in ['build', 'Build', 'Debug', 'Release']]
            
            for file in files:
                if file.endswith(('.c', '.h')):
                    filepath = os.path.join(root, file)
                    self.parse_file(filepath)
        
        print(f"✅ Found {len(self.functions)} functions")
    
    def parse_file(self, filepath: str):
        """Parse single C file for function definitions and calls"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return
        
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        
        # Find function definitions
        func_pattern = r'^\s*(?:static\s+)?(?:inline\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{'
        
        lines = content.split('\n')
        current_func = None
        brace_count = 0
        func_start_line = 0
        
        for line_num, line in enumerate(lines, 1):
            # Check for function definition
            match = re.match(func_pattern, line)
            if match and brace_count == 0:
                func_name = match.group(1)
                
                # Skip common non-functions
                if func_name in ['if', 'while', 'for', 'switch']:
                    continue
                
                current_func = FunctionInfo(func_name, filepath, line_num)
                func_start_line = line_num
                self.functions[func_name] = current_func
            
            # Track braces to know when function ends
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            if current_func:
                current_func.line_count += 1
                
                # Find function calls within this function
                call_pattern = r'\b(\w+)\s*\('
                for match in re.finditer(call_pattern, line):
                    called_func = match.group(1)
                    # Exclude C keywords and macros
                    if called_func not in ['if', 'while', 'for', 'switch', 'return', 'sizeof']:
                        current_func.calls_to.add(called_func)
                
                # Estimate local variable size
                var_pattern = r'\b(uint32_t|uint16_t|uint8_t|int|char)\s+\w+(\[\d+\])?'
                for match in re.finditer(var_pattern, line):
                    var_type = match.group(1)
                    array_size = match.group(2)
                    
                    # Estimate size
                    type_sizes = {
                        'uint32_t': 4, 'int': 4,
                        'uint16_t': 2,
                        'uint8_t': 1, 'char': 1
                    }
                    size = type_sizes.get(var_type, 4)
                    
                    if array_size:
                        # Extract array size
                        arr_match = re.search(r'\[(\d+)\]', array_size)
                        if arr_match:
                            size *= int(arr_match.group(1))
                    
                    current_func.local_vars_size += size
            
            # Function ended
            if brace_count == 0 and current_func:
                current_func = None
    
    def build_call_graph(self):
        """Build caller-callee relationships"""
        print("🔗 Building call graph...")
        
        for func_name, func_info in self.functions.items():
            for called_name in func_info.calls_to:
                if called_name in self.functions:
                    self.functions[called_name].called_from.add(func_name)
    
    def calculate_max_depth(self, start_func='main'):
        """Calculate maximum call depth using BFS"""
        print(f"📊 Calculating call depths from {start_func}()...")
        
        if start_func not in self.functions:
            print(f"⚠️  Function '{start_func}' not found, trying alternative entry points...")
            # Try common alternatives
            for alt in ['main', 'system_main_loop', 'slaveClockRun']:
                if alt in self.functions:
                    start_func = alt
                    break
        
        # BFS to find depths
        queue = deque([(start_func, 0)])
        visited = set()
        
        while queue:
            func_name, depth = queue.popleft()
            
            if func_name not in self.functions:
                continue
            
            func = self.functions[func_name]
            func.max_depth = max(func.max_depth, depth)
            
            if func_name in visited:
                continue
            visited.add(func_name)
            
            # Enqueue callees
            for callee in func.calls_to:
                queue.append((callee, depth + 1))
    
    def find_inline_candidates(self) -> List[Tuple[str, int]]:
        """Identify functions that should be inlined"""
        print("🎯 Identifying inline candidates...")
        
        candidates = []
        
        for func_name, func in self.functions.items():
            # Skip main and interrupt handlers
            if func_name in ['main', 'main_loop'] or 'IRQHandler' in func_name:
                continue
            
            # Calculate priority score
            priority = 0
            reason = []
            
            # Depth factor (most important)
            if func.max_depth > 6:
                priority += 100
                reason.append(f"Very deep (depth={func.max_depth})")
            elif func.max_depth > 5:
                priority += 50
                reason.append(f"Deep (depth={func.max_depth})")
            elif func.max_depth > 4:
                priority += 20
                reason.append(f"Moderately deep (depth={func.max_depth})")
            
            # Size factor
            if func.line_count < 15:
                priority += 40
                reason.append(f"Small ({func.line_count} lines)")
            elif func.line_count < 25:
                priority += 20
                reason.append("Medium size")
            elif func.line_count < 30:
                priority += 10
                reason.append("Acceptable size")
            else:
                priority -= 20
                reason.append(f"Too large ({func.line_count} lines)")
            
            # Call count factor
            call_count = len(func.called_from)
            if call_count == 1:
                priority += 30
                reason.append("Called once")
            elif call_count == 2:
                priority += 15
                reason.append("Called twice")
            elif call_count == 3:
                priority += 5
                reason.append("Called 3x")
            else:
                priority -= 10
                reason.append(f"Called {call_count}x (duplication risk)")
            
            # Local vars factor
            if func.local_vars_size > 128:
                priority -= 30
                reason.append(f"Large locals ({func.local_vars_size}B)")
            elif func.local_vars_size > 64:
                priority -= 10
            
            # Only consider if priority is positive
            if priority > 0:
                candidates.append((func_name, priority, reason))
        
        # Sort by priority (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates
    
    def calculate_stack_savings(self, func_name: str) -> int:
        """Estimate stack savings if function is inlined"""
        if func_name not in self.functions:
            return 0
        
        func = self.functions[func_name]
        
        # Frame overhead (saved per inline)
        frame_overhead = 32
        
        # Local variables (may or may not be saved, conservative estimate)
        local_savings = func.local_vars_size // 2
        
        # Total savings
        savings = frame_overhead + local_savings
        
        return savings
    
    def generate_report(self, output_file='stack_analysis_report.md'):
        """Generate comprehensive markdown report"""
        print(f"📝 Generating report: {output_file}")
        
        candidates = self.find_inline_candidates()
        
        with open(output_file, 'w') as f:
            # Executive summary
            f.write("# Stack Optimization Analysis Report\n\n")
            f.write(f"**Total Functions Analyzed**: {len(self.functions)}\n")
            f.write(f"**Inline Candidates Found**: {len(candidates)}\n\n")
            
            high = sum(1 for _, p, _ in candidates if p >= 100)
            medium = sum(1 for _, p, _ in candidates if 50 <= p < 100)
            low = sum(1 for _, p, _ in candidates if p < 50)
            
            f.write(f"- 🔴 HIGH Priority: {high} functions\n")
            f.write(f"- 🟡 MEDIUM Priority: {medium} functions\n")
            f.write(f"- 🟢 LOW Priority: {low} functions\n\n")
            
            total_savings = sum(self.calculate_stack_savings(name) for name, _, _ in candidates[:10])
            f.write(f"**Potential Stack Savings (Top 10)**: ~{total_savings} bytes\n\n")
            
            f.write("---\n\n")
            
            # Top 10 detailed analysis
            f.write("## Top 10 Inline Candidates\n\n")
            
            for i, (func_name, priority, reasons) in enumerate(candidates[:10], 1):
                func = self.functions[func_name]
                savings = self.calculate_stack_savings(func_name)
                
                # Priority label
                if priority >= 100:
                    priority_label = "🔴 HIGH"
                elif priority >= 50:
                    priority_label = "🟡 MEDIUM"
                else:
                    priority_label = "🟢 LOW"
                
                f.write(f"### {i}. Function: `{func_name}()`\n\n")
                f.write(f"**📍 Location**: `{os.path.basename(func.file)}:{func.line}`\n\n")
                f.write(f"**📊 Metrics**:\n")
                f.write(f"- Call Depth: {func.max_depth} levels\n")
                f.write(f"- Function Size: {func.line_count} lines\n")
                f.write(f"- Local Variables: ~{func.local_vars_size} bytes\n")
                f.write(f"- Called From: {len(func.called_from)} locations\n")
                f.write(f"- Stack Frame Cost: ~32 bytes\n\n")
                
                f.write(f"**💾 Stack Impact**:\n")
                f.write(f"- Estimated Savings: **~{savings} bytes**\n\n")
                
                f.write(f"**🎚️ Priority**: {priority_label} (score: {priority})\n\n")
                
                f.write(f"**📝 Rationale**:\n")
                for reason in reasons:
                    f.write(f"- {reason}\n")
                
                f.write("\n---\n\n")
            
            # Summary table
            f.write("## Summary Table\n\n")
            f.write("| # | Function | Location | Depth | Size | Calls | Savings | Priority |\n")
            f.write("|---|----------|----------|-------|------|-------|---------|----------|\n")
            
            for i, (func_name, priority, _) in enumerate(candidates[:20], 1):
                func = self.functions[func_name]
                savings = self.calculate_stack_savings(func_name)
                
                if priority >= 100:
                    pri = "HIGH"
                elif priority >= 50:
                    pri = "MEDIUM"
                else:
                    pri = "LOW"
                
                f.write(f"| {i} | {func_name}() | {os.path.basename(func.file)}:{func.line} | "
                       f"{func.max_depth} | {func.line_count} | {len(func.called_from)} | "
                       f"{savings}B | {pri} |\n")
            
            f.write(f"\n**Total Potential Savings**: ~{total_savings} bytes\n")
        
        print(f"✅ Report generated: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_call_depth.py <source_directory>")
        print("\nAnalyzes C source code to identify inline candidates and calculate stack savings.")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    
    if not os.path.isdir(source_dir):
        print(f"Error: {source_dir} is not a valid directory")
        sys.exit(1)
    
    analyzer = CallGraphAnalyzer(source_dir)
    analyzer.scan_sources()
    analyzer.build_call_graph()
    analyzer.calculate_max_depth()
    analyzer.generate_report()
    
    print("\n🎉 Analysis complete!")

if __name__ == '__main__':
    main()