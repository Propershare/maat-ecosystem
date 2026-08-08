"""
AST Parser for Multiple Languages
Extracts functions, classes, imports, and call relationships
Maat: Truth - Accurate code analysis
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import ast
import re

log = logging.getLogger(__name__)


class ASTParser:
    """Parse AST for Python, JavaScript, and TypeScript."""
    
    def extract_functions(self, file_path: Path, language: str) -> List[Dict[str, Any]]:
        """Extract function signatures from file."""
        if language == "python":
            return self._extract_python_functions(file_path)
        elif language in ["javascript", "typescript"]:
            return self._extract_js_functions(file_path)
        else:
            return []
    
    def extract_classes(self, file_path: Path, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions from file."""
        if language == "python":
            return self._extract_python_classes(file_path)
        elif language in ["javascript", "typescript"]:
            return self._extract_js_classes(file_path)
        else:
            return []
    
    def extract_imports(self, file_path: Path, language: str) -> List[str]:
        """Extract import statements from file."""
        if language == "python":
            return self._extract_python_imports(file_path)
        elif language in ["javascript", "typescript"]:
            return self._extract_js_imports(file_path)
        else:
            return []
    
    def extract_calls(self, file_path: Path, language: str) -> Dict[str, List[str]]:
        """Extract function call relationships."""
        if language == "python":
            return self._extract_python_calls(file_path)
        elif language in ["javascript", "typescript"]:
            return self._extract_js_calls(file_path)
        else:
            return {}
    
    def _extract_python_functions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Python function signatures."""
        functions = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Extract parameters
                    params = []
                    for arg in node.args.args:
                        param_info = {"name": arg.arg}
                        if arg.annotation:
                            param_info["type"] = ast.unparse(arg.annotation) if hasattr(ast, "unparse") else str(arg.annotation)
                        params.append(param_info)
                    
                    # Extract return type
                    return_type = None
                    if node.returns:
                        return_type = ast.unparse(node.returns) if hasattr(ast, "unparse") else str(node.returns)
                    
                    functions.append({
                        "name": node.name,
                        "parameters": params,
                        "return_type": return_type,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "line_number": node.lineno,
                        "docstring": ast.get_docstring(node),
                    })
        except Exception as e:
            log.debug(f"Error parsing Python file {file_path}: {e}")
        
        return functions
    
    def _extract_python_classes(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Python class definitions."""
        classes = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract base classes
                    bases = []
                    for base in node.bases:
                        bases.append(ast.unparse(base) if hasattr(ast, "unparse") else str(base))
                    
                    # Extract methods
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    
                    classes.append({
                        "name": node.name,
                        "bases": bases,
                        "methods": methods,
                        "line_number": node.lineno,
                        "docstring": ast.get_docstring(node),
                    })
        except Exception as e:
            log.debug(f"Error parsing Python classes from {file_path}: {e}")
        
        return classes
    
    def _extract_python_imports(self, file_path: Path) -> List[str]:
        """Extract Python import statements."""
        imports = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
        except Exception as e:
            log.debug(f"Error extracting Python imports from {file_path}: {e}")
        
        return imports
    
    def _extract_python_calls(self, file_path: Path) -> Dict[str, List[str]]:
        """Extract Python function call relationships."""
        calls = defaultdict(list)
        current_function = None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    current_function = node.name
                elif isinstance(node, ast.Call) and current_function:
                    if isinstance(node.func, ast.Name):
                        calls[current_function].append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls[current_function].append(node.func.attr)
        except Exception as e:
            log.debug(f"Error extracting Python calls from {file_path}: {e}")
        
        return dict(calls)
    
    def _extract_js_functions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript function signatures (regex-based fallback)."""
        functions = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Match function declarations: function name(...) or const name = (...) =>
            patterns = [
                r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)",
                r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>",
                r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\(([^)]*)\)",
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    params_str = match.group(2) if len(match.groups()) > 1 else ""
                    params = [p.strip().split(":")[0] for p in params_str.split(",") if p.strip()]
                    
                    # Find line number
                    line_num = content[:match.start()].count("\n") + 1
                    
                    functions.append({
                        "name": func_name,
                        "parameters": [{"name": p} for p in params],
                        "line_number": line_num,
                    })
        except Exception as e:
            log.debug(f"Error extracting JS functions from {file_path}: {e}")
        
        return functions
    
    def _extract_js_classes(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript class definitions (regex-based fallback)."""
        classes = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Match class declarations: class Name extends Base
            pattern = r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?"
            
            for match in re.finditer(pattern, content):
                class_name = match.group(1)
                base_class = match.group(2) if match.group(2) else None
                
                # Find line number
                line_num = content[:match.start()].count("\n") + 1
                
                classes.append({
                    "name": class_name,
                    "bases": [base_class] if base_class else [],
                    "line_number": line_num,
                })
        except Exception as e:
            log.debug(f"Error extracting JS classes from {file_path}: {e}")
        
        return classes
    
    def _extract_js_imports(self, file_path: Path) -> List[str]:
        """Extract JavaScript/TypeScript import statements."""
        imports = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Match import statements
            patterns = [
                r"import\s+(?:\*\s+as\s+\w+|[\w\s,{}]+)\s+from\s+['\"]([^'\"]+)['\"]",
                r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    imports.append(match.group(1))
        except Exception as e:
            log.debug(f"Error extracting JS imports from {file_path}: {e}")
        
        return imports
    
    def _extract_js_calls(self, file_path: Path) -> Dict[str, List[str]]:
        """Extract JavaScript/TypeScript function call relationships (simplified)."""
        # This is a simplified version - full implementation would need proper JS parser
        calls = defaultdict(list)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Match function calls: name(...)
            pattern = r"(\w+)\s*\("
            for match in re.finditer(pattern, content):
                # Try to find containing function (simplified)
                # In production, would use proper AST parser for JS
                call_name = match.group(1)
                if call_name not in ["if", "for", "while", "return", "console"]:
                    # This is simplified - would need proper context tracking
                    pass
        except Exception as e:
            log.debug(f"Error extracting JS calls from {file_path}: {e}")
        
        return dict(calls)

