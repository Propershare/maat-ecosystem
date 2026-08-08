"""
Codebase Structure Builder
Layer 1: Build complete codebase structure (fits in context)
Maat: Order - Structured representation of codebase
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from collections import defaultdict

from .ast_parser import ASTParser

log = logging.getLogger(__name__)


class CodebaseStructureBuilder:
    """
    Builds structured representation of entire codebase.
    Output: 10-50KB JSON (fits in context easily)
    """
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        if not self.codebase_path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")
        
        self.ast_parser = ASTParser()
        self.structure = {
            "files": [],
            "modules": {},
            "dependencies": {},
            "functions": [],
            "classes": [],
            "imports": {},
            "call_graph": {},
            "metadata": {},
        }
    
    def build(self) -> Dict[str, Any]:
        """
        Build complete codebase structure.
        
        Returns:
            Dictionary with file tree, functions, classes, dependencies, call graph
        """
        log.info(f"Building codebase structure for: {self.codebase_path}")
        
        # 1. Scan all files
        files = self._scan_files()
        self.structure["files"] = files
        
        # 2. Extract modules
        modules = self._extract_modules(files)
        self.structure["modules"] = modules
        
        # 3. Build dependency graph
        dependencies = self._build_dependency_graph(files)
        self.structure["dependencies"] = dependencies
        
        # 4. Extract function signatures
        functions = self._extract_function_signatures(files)
        self.structure["functions"] = functions
        
        # 5. Extract class definitions
        classes = self._extract_class_definitions(files)
        self.structure["classes"] = classes
        
        # 6. Map imports
        imports = self._map_imports(files)
        self.structure["imports"] = imports
        
        # 7. Build call graph
        call_graph = self._build_call_graph(files, functions)
        self.structure["call_graph"] = call_graph
        
        # 8. Calculate metadata
        metadata = self._calculate_metadata(files, functions, classes)
        self.structure["metadata"] = metadata
        
        log.info(f"Structure built: {len(files)} files, {len(functions)} functions, {len(classes)} classes")
        return self.structure
    
    def _scan_files(self) -> List[Dict[str, Any]]:
        """Scan all code files in codebase."""
        files = []
        code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".cpp", ".c"}
        
        for file_path in self.codebase_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    stat = file_path.stat()
                    files.append({
                        "path": str(file_path.relative_to(self.codebase_path)),
                        "absolute_path": str(file_path),
                        "size": stat.st_size,
                        "extension": file_path.suffix,
                        "language": self._detect_language(file_path.suffix),
                    })
                except Exception as e:
                    log.debug(f"Error scanning file {file_path}: {e}")
        
        return sorted(files, key=lambda x: x["path"])
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
        }
        return lang_map.get(extension, "unknown")
    
    def _extract_modules(self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract module structure."""
        modules = defaultdict(list)
        
        for file_info in files:
            path = Path(file_info["path"])
            # Group by directory (module)
            module = str(path.parent) if path.parent != Path(".") else "root"
            modules[module].append(file_info["path"])
        
        return dict(modules)
    
    def _build_dependency_graph(self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build dependency graph from imports."""
        dependencies = defaultdict(list)
        
        for file_info in files:
            if file_info["language"] not in ["python", "javascript", "typescript"]:
                continue
            
            file_path = self.codebase_path / file_info["path"]
            try:
                imports = self.ast_parser.extract_imports(file_path, file_info["language"])
                dependencies[file_info["path"]] = imports
            except Exception as e:
                log.debug(f"Error extracting imports from {file_path}: {e}")
        
        return dict(dependencies)
    
    def _extract_function_signatures(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract function signatures from all files."""
        functions = []
        
        for file_info in files:
            if file_info["language"] not in ["python", "javascript", "typescript"]:
                continue
            
            file_path = self.codebase_path / file_info["path"]
            try:
                file_functions = self.ast_parser.extract_functions(file_path, file_info["language"])
                for func in file_functions:
                    func["file"] = file_info["path"]
                    functions.append(func)
            except Exception as e:
                log.debug(f"Error extracting functions from {file_path}: {e}")
        
        return functions
    
    def _extract_class_definitions(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract class definitions from all files."""
        classes = []
        
        for file_info in files:
            if file_info["language"] not in ["python", "javascript", "typescript"]:
                continue
            
            file_path = self.codebase_path / file_info["path"]
            try:
                file_classes = self.ast_parser.extract_classes(file_path, file_info["language"])
                for cls in file_classes:
                    cls["file"] = file_info["path"]
                    classes.append(cls)
            except Exception as e:
                log.debug(f"Error extracting classes from {file_path}: {e}")
        
        return classes
    
    def _map_imports(self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Map all imports in codebase."""
        imports_map = {}
        
        for file_info in files:
            if file_info["language"] not in ["python", "javascript", "typescript"]:
                continue
            
            file_path = self.codebase_path / file_info["path"]
            try:
                imports = self.ast_parser.extract_imports(file_path, file_info["language"])
                imports_map[file_info["path"]] = imports
            except Exception as e:
                log.debug(f"Error mapping imports from {file_path}: {e}")
        
        return imports_map
    
    def _build_call_graph(self, files: List[Dict[str, Any]], functions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build call graph showing function call relationships."""
        call_graph = defaultdict(list)
        
        # Create function lookup
        func_lookup = {f"{f['file']}::{f['name']}": f for f in functions}
        
        for file_info in files:
            if file_info["language"] not in ["python", "javascript", "typescript"]:
                continue
            
            file_path = self.codebase_path / file_info["path"]
            try:
                calls = self.ast_parser.extract_calls(file_path, file_info["language"])
                for caller, callees in calls.items():
                    caller_key = f"{file_info['path']}::{caller}"
                    call_graph[caller_key] = callees
            except Exception as e:
                log.debug(f"Error building call graph from {file_path}: {e}")
        
        return dict(call_graph)
    
    def _calculate_metadata(self, files: List[Dict[str, Any]], functions: List[Dict[str, Any]], classes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate codebase metadata."""
        total_size = sum(f["size"] for f in files)
        languages = {}
        for f in files:
            lang = f["language"]
            languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "total_files": len(files),
            "total_functions": len(functions),
            "total_classes": len(classes),
            "total_size_bytes": total_size,
            "languages": languages,
            "complexity": {
                "avg_functions_per_file": len(functions) / len(files) if files else 0,
                "avg_classes_per_file": len(classes) / len(files) if files else 0,
            },
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert structure to JSON string."""
        return json.dumps(self.structure, indent=indent)
    
    def get_size(self) -> int:
        """Get size of structure in bytes."""
        return len(self.to_json().encode("utf-8"))

