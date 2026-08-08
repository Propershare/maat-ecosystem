"""
Project Discovery System
Maat: Truth - Know what exists before suggesting changes
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

log = logging.getLogger(__name__)


class ProjectDiscovery:
    """
    Auto-discover project structure and suggest builds/changes.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovery_cache: Optional[Dict[str, Any]] = None
    
    def discover_project(self) -> Dict[str, Any]:
        """
        Discover complete project structure.
        
        Returns:
            {
                "components": Dict[str, Any],
                "missing": List[str],
                "suggestions": List[str],
                "patterns": Dict[str, Any]
            }
        """
        if self.discovery_cache:
            return self.discovery_cache
        
        discovery = {
            "components": {},
            "missing": [],
            "suggestions": [],
            "patterns": {}
        }
        
        # Discover core components
        discovery["components"]["core"] = self._discover_core()
        discovery["components"]["api"] = self._discover_api()
        discovery["components"]["maat_memory"] = self._discover_maat_memory()
        discovery["components"]["docs"] = self._discover_docs()
        
        # Find missing components
        discovery["missing"] = self._find_missing(discovery["components"])
        
        # Generate suggestions
        discovery["suggestions"] = self._generate_suggestions(discovery)
        
        # Discover patterns
        discovery["patterns"] = self._discover_patterns()
        
        self.discovery_cache = discovery
        return discovery
    
    def _discover_core(self) -> Dict[str, Any]:
        """Discover core components."""
        core_dir = self.project_root / "core"
        components = {
            "exists": core_dir.exists(),
            "subdirs": [],
            "files": [],
            "governance": False,
            "maatcode": False,
            "integrations": False
        }
        
        if core_dir.exists():
            for item in core_dir.iterdir():
                if item.is_dir():
                    components["subdirs"].append(item.name)
                    if item.name == "governance":
                        components["governance"] = True
                        components["governance_files"] = [f.name for f in item.glob("*.py")]
                    elif item.name == "maatcode":
                        components["maatcode"] = True
                        components["maatcode_files"] = [f.name for f in item.glob("*.py")]
                    elif item.name == "integrations":
                        components["integrations"] = True
                        components["integrations_files"] = [f.name for f in item.glob("*.py")]
                elif item.is_file() and item.suffix == ".py":
                    components["files"].append(item.name)
        
        return components
    
    def _discover_api(self) -> Dict[str, Any]:
        """Discover API components."""
        api_dir = self.project_root / "api"
        components = {
            "exists": api_dir.exists(),
            "files": [],
            "endpoints": []
        }
        
        if api_dir.exists():
            for item in api_dir.iterdir():
                if item.is_file() and item.suffix == ".py":
                     components["files"].append(item.name)
                     # Try to detect endpoints (simple heuristic)
                     try:
                         content = item.read_text()
                         if "@app.post" in content or "@app.get" in content:
                             components["endpoints"].append(item.name)
                     except (UnicodeDecodeError, OSError):
                         pass
        
        return components
    
    def _discover_maat_memory(self) -> Dict[str, Any]:
        """Discover Maat Memory system."""
        mm_dir = self.project_root / "maat_memory"
        components = {
            "exists": mm_dir.exists(),
            "files": [],
            "has_postgres": False,
            "has_auto_setup": False,
            "has_standards": False
        }
        
        if mm_dir.exists():
            components["files"] = [f.name for f in mm_dir.glob("*.py")]
            components["has_postgres"] = (mm_dir / "memory_postgres.py").exists()
            components["has_auto_setup"] = (mm_dir / "auto_setup.py").exists()
            components["has_standards"] = (mm_dir / "standards.py").exists()
        
        return components
    
    def _discover_docs(self) -> Dict[str, Any]:
        """Discover documentation."""
        docs_dir = self.project_root / "docs"
        components = {
            "exists": docs_dir.exists(),
            "files": [],
            "has_index": False
        }
        
        if docs_dir.exists():
            components["files"] = [f.name for f in docs_dir.glob("*.md")]
            components["has_index"] = (docs_dir / "INDEX.md").exists()
        
        return components
    
    def _find_missing(self, components: Dict[str, Any]) -> List[str]:
        """Find missing critical components."""
        missing = []
        
        # Check governance
        if not components.get("core", {}).get("governance"):
            missing.append("core/governance/ - Three-ring, TehutiGuard")
        
        # Check maatcode
        if not components.get("core", {}).get("maatcode"):
            missing.append("core/maatcode/ - Code analysis")
        
        # Check integrations
        if not components.get("core", {}).get("integrations"):
            missing.append("core/integrations/ - PostgreSQL, Redis, Ollama")
        
        # Check API
        if not components.get("api", {}).get("exists"):
            missing.append("api/ - API endpoints")
        
        return missing
    
    def _generate_suggestions(self, discovery: Dict[str, Any]) -> List[str]:
        """Generate build suggestions based on what exists."""
        suggestions = []
        components = discovery["components"]
        
        # If governance missing, suggest it
        if not components.get("core", {}).get("governance"):
            suggestions.append("Build core/governance/ - ThreeRingClassifier, TehutiGuard, AuditTrail")
        
        # If maatcode missing, suggest it
        if not components.get("core", {}).get("maatcode"):
            suggestions.append("Build core/maatcode/ - CodeEmbedder, SemanticSearch, PatternDetector")
        
        # If API missing, suggest it
        if not components.get("api", {}).get("exists"):
            suggestions.append("Build api/ - FastAPI endpoints for RAG, agent runs")
        
        # Check for incomplete implementations
        if components.get("core", {}).get("governance"):
            gov_files = components["core"].get("governance_files", [])
            if "three_ring.py" not in gov_files:
                suggestions.append("Complete core/governance/three_ring.py")
            if "tehuti_guard.py" not in gov_files:
                suggestions.append("Complete core/governance/tehuti_guard.py")
        
        return suggestions
    
    def _discover_patterns(self) -> Dict[str, Any]:
        """Discover code patterns for consistency."""
        patterns = {
            "imports": [],
            "structure": [],
            "naming": []
        }
        
        # Discover import patterns
        core_dir = self.project_root / "core"
        if core_dir.exists():
            for py_file in core_dir.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    # Check for common imports
                    if "from maat_memory import" in content:
                        patterns["imports"].append("maat_memory")
                    if "from typing import" in content:
                        patterns["imports"].append("typing")
                    if "import logging" in content:
                        patterns["imports"].append("logging")
                except (UnicodeDecodeError, OSError):
                    pass
        
        return patterns
    
    def get_suggestions(self) -> List[str]:
        """Get build suggestions."""
        discovery = self.discover_project()
        return discovery["suggestions"]
    
    def get_missing(self) -> List[str]:
        """Get missing components."""
        discovery = self.discover_project()
        return discovery["missing"]


def discover_project(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Convenience function to discover project."""
    if project_root is None:
        project_root = Path.cwd()
        # Find project root
        for path in [project_root] + list(project_root.parents):
            if (path / "AGENTS.md").exists() or (path / "maat_memory").exists():
                project_root = path
                break
    
    discovery = ProjectDiscovery(project_root)
    return discovery.discover_project()

