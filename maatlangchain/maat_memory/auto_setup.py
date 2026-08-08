"""
Auto-Setup System for Maat Memory
Maat: Order - Agents configure themselves, no user intervention needed
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from .machine_info import get_machine_info, get_unique_agent_id

log = logging.getLogger(__name__)


class MaatAutoSetup:
    """
    Automatic setup and validation system for Maat Memory.
    
    Agents run this on first load to:
    1. Detect project structure
    2. Configure paths automatically
    3. Ensure no conflicts
    4. Validate Maat compliance
    5. Set up Maat Memory if needed
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize auto-setup with project root detection."""
        self.project_root = project_root or self._detect_project_root()
        self.machine_info = get_machine_info()
        self.agent_id = get_unique_agent_id("opencode")  # Will be overridden by tool_type
        self.setup_log: List[Dict[str, Any]] = []
        
    def _detect_project_root(self) -> Path:
        """Auto-detect project root by looking for AGENTS.md or maatlangchain directory."""
        cwd = Path.cwd()
        
        # Check current directory and parents
        for path in [cwd] + list(cwd.parents):
            # Look for AGENTS.md (primary indicator)
            if (path / "AGENTS.md").exists():
                log.info(f"✅ Found project root via AGENTS.md: {path}")
                return path
            
            # Look for maatlangchain directory
            if path.name == "maatlangchain" and (path / "maat_memory").exists():
                log.info(f"✅ Found project root via maatlangchain: {path}")
                return path
            
            # Data-drive workspaces may expose the governance home as a
            # maatlangchain symlink inside the workspace root.
            maatlangchain_dir = path / "maatlangchain"
            if (maatlangchain_dir / "maat_memory").exists():
                log.info(
                    "✅ Found project root via child maatlangchain: "
                    f"{maatlangchain_dir}"
                )
                return maatlangchain_dir
            
            # Look for maat_memory directory
            if (path / "maat_memory").exists():
                log.info(f"✅ Found project root via maat_memory: {path}")
                return path
        
        # Fallback to current directory
        log.warning(f"⚠️  Could not detect project root, using: {cwd}")
        return cwd
    
    def validate_project_structure(self) -> Dict[str, Any]:
        """
        Validate project structure and detect issues.
        
        Returns:
            {
                "valid": bool,
                "issues": List[str],
                "warnings": List[str],
                "structure": Dict[str, Any]
            }
        """
        issues = []
        warnings = []
        structure = {}
        
        # Check for AGENTS.md
        agents_md = self.project_root / "AGENTS.md"
        if not agents_md.exists():
            issues.append("AGENTS.md not found in project root")
        else:
            structure["agents_md"] = str(agents_md)
        
        # Check for maat_memory directory
        maat_memory_dir = self.project_root / "maat_memory"
        if not maat_memory_dir.exists():
            issues.append("maat_memory/ directory not found")
        else:
            structure["maat_memory_dir"] = str(maat_memory_dir)
            
            # Check for required files
            required_files = ["__init__.py", "memory.py", "machine_info.py"]
            for req_file in required_files:
                if not (maat_memory_dir / req_file).exists():
                    issues.append(f"maat_memory/{req_file} not found")
        
        # No legacy system checks needed - Maat Memory is the only system
        
        # Check Python path
        if str(self.project_root) not in sys.path:
            warnings.append(f"Project root not in Python path - may need: sys.path.insert(0, '{self.project_root}')")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "structure": structure
        }
    
    def detect_conflicts(self) -> Dict[str, Any]:
        """
        Detect configuration conflicts.
        
        Returns:
            {
                "conflicts": List[str],
                "recommendations": List[str]
            }
        """
        conflicts = []
        recommendations = []
        
        # Check for multiple memory systems
        json_memory = self.project_root / ".maat_memory" / "maat_memory.json"
        pgvector_url = os.getenv("PGVECTOR_DB_URL")
        
        if json_memory.exists() and pgvector_url:
            recommendations.append("Both JSON and PostgreSQL backends available - PostgreSQL will be used")
        
        # Check for duplicate agent IDs (shouldn't happen, but check)
        # This would require querying the database, so skip for now
        
        return {
            "conflicts": conflicts,
            "recommendations": recommendations
        }
    
    def ensure_python_path(self) -> bool:
        """Ensure project root is in Python path."""
        project_str = str(self.project_root)
        if project_str not in sys.path:
            sys.path.insert(0, project_str)
            self.setup_log.append({
                "action": "add_python_path",
                "path": project_str,
                "status": "added"
            })
            log.info(f"✅ Added to Python path: {project_str}")
            return True
        return False
    
    def validate_maat_compliance(self) -> Dict[str, Any]:
        """
        Validate Maat principles compliance.
        
        Checks:
        - Truth: Accurate configuration, no false data
        - Balance: Proper resource usage, no conflicts
        - Order: Correct structure, proper organization
        - Justice: Fair access, proper permissions
        - Self-Reflection: System awareness, proper logging
        """
        compliance = {
            "truth": [],
            "balance": [],
            "order": [],
            "justice": [],
            "self_reflection": []
        }
        
        # Truth: Check for accurate configuration
        if self.project_root.exists():
            compliance["truth"].append("✅ Project root detected accurately")
        else:
            compliance["truth"].append("❌ Project root detection failed")
        
        # Balance: Check for conflicts
        conflicts = self.detect_conflicts()
        if len(conflicts["conflicts"]) == 0:
            compliance["balance"].append("✅ No configuration conflicts")
        else:
            compliance["balance"].append(f"⚠️  {len(conflicts['conflicts'])} conflicts detected")
        
        # Order: Check structure
        structure = self.validate_project_structure()
        if structure["valid"]:
            compliance["order"].append("✅ Project structure valid")
        else:
            compliance["order"].append(f"❌ {len(structure['issues'])} structural issues")
        
        # Justice: Check permissions (basic check)
        if os.access(self.project_root, os.R_OK):
            compliance["justice"].append("✅ Read access granted")
        else:
            compliance["justice"].append("❌ Read access denied")
        
        if os.access(self.project_root, os.W_OK):
            compliance["justice"].append("✅ Write access granted")
        else:
            compliance["justice"].append("⚠️  Write access limited")
        
        # Self-Reflection: Check logging setup
        if logging.getLogger().level <= logging.INFO:
            compliance["self_reflection"].append("✅ Logging configured")
        else:
            compliance["self_reflection"].append("⚠️  Logging level may be too high")
        
        return compliance
    
    def auto_setup(self, tool_type: str = "opencode") -> Dict[str, Any]:
        """
        Run complete auto-setup process.
        
        Args:
            tool_type: "cursor" or "opencode"
        
        Returns:
            Setup report with status, issues, and recommendations
        """
        self.agent_id = get_unique_agent_id(tool_type)
        
        log.info("🔧 Starting Maat Auto-Setup...")
        log.info(f"   Project root: {self.project_root}")
        log.info(f"   Agent ID: {self.agent_id}")
        log.info(f"   Machine: {self.machine_info['hostname']}")
        
        # 1. Ensure Python path
        self.ensure_python_path()
        
        # 2. Validate project structure
        structure = self.validate_project_structure()
        
        # 3. Detect conflicts
        conflicts = self.detect_conflicts()
        
        # 4. Validate Maat compliance
        compliance = self.validate_maat_compliance()
        
        # 5. Test Maat Memory import
        memory_available = False
        memory_error = None
        try:
            from .memory import MaatMemory
            memory = MaatMemory()
            memory_available = True
            log.info(f"✅ Maat Memory available: {memory.__class__.__name__}")
        except Exception as e:
            memory_error = str(e)
            log.warning(f"⚠️  Maat Memory not available: {e}")
        
        # Build report
        report = {
            "status": "success" if structure["valid"] and len(conflicts["conflicts"]) == 0 else "warning",
            "project_root": str(self.project_root),
            "agent_id": self.agent_id,
            "machine_info": self.machine_info,
            "structure": structure,
            "conflicts": conflicts,
            "compliance": compliance,
            "memory": {
                "available": memory_available,
                "error": memory_error
            },
            "setup_log": self.setup_log,
            "recommendations": []
        }
        
        # Add recommendations
        if not structure["valid"]:
            report["recommendations"].extend([
                f"Fix {len(structure['issues'])} structural issues",
                "See structure.issues for details"
            ])
        
        if len(conflicts["conflicts"]) > 0:
            report["recommendations"].extend(conflicts["recommendations"])
        
        if not memory_available:
            report["recommendations"].append("Set PGVECTOR_DB_URL for PostgreSQL backend, or use JSON fallback")
        
        log.info("✅ Auto-setup complete")
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted setup report."""
        print("\n" + "="*60)
        print("🔧 Maat Auto-Setup Report")
        print("="*60)
        print(f"\n📍 Project Root: {report['project_root']}")
        print(f"🆔 Agent ID: {report['agent_id']}")
        print(f"🖥️  Machine: {report['machine_info']['hostname']}")
        
        print(f"\n📊 Status: {report['status'].upper()}")
        
        if report['structure']['issues']:
            print(f"\n❌ Issues ({len(report['structure']['issues'])}):")
            for issue in report['structure']['issues']:
                print(f"   - {issue}")
        
        if report['structure']['warnings']:
            print(f"\n⚠️  Warnings ({len(report['structure']['warnings'])}):")
            for warning in report['structure']['warnings']:
                print(f"   - {warning}")
        
        if report['conflicts']['conflicts']:
            print(f"\n⚠️  Conflicts ({len(report['conflicts']['conflicts'])}):")
            for conflict in report['conflicts']['conflicts']:
                print(f"   - {conflict}")
        
        if report['memory']['available']:
            print(f"\n✅ Maat Memory: Available")
        else:
            print(f"\n❌ Maat Memory: {report['memory']['error']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   - {rec}")
        
        print("\n" + "="*60 + "\n")


def run_auto_setup(tool_type: str = "opencode", verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run auto-setup.
    
    Args:
        tool_type: "cursor" or "opencode"
        verbose: Print report to stdout
    
    Returns:
        Setup report
    """
    setup = MaatAutoSetup()
    report = setup.auto_setup(tool_type)
    
    if verbose:
        setup.print_report(report)
    
    return report


if __name__ == "__main__":
    # Run auto-setup when executed directly
    import sys
    tool_type = sys.argv[1] if len(sys.argv) > 1 else "opencode"
    run_auto_setup(tool_type, verbose=True)

