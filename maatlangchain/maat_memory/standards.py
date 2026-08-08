"""
Maat Standards for Core Component Building
Maat: Order - Consistent standards for all components
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import ast
import logging

log = logging.getLogger(__name__)


class MaatStandards:
    """
    Standards validator for core components.
    
    Ensures all components follow Maat principles:
    - Truth: Accurate, validated
    - Balance: No conflicts, efficient
    - Order: Consistent structure
    - Justice: Fair access, proper permissions
    - Self-Reflection: Logging, error handling
    """
    
    @staticmethod
    def validate_component_structure(component_path: Path) -> Dict[str, Any]:
        """
        Validate component follows standard structure.
        
        Expected structure:
        component_name/
        ├── __init__.py
        ├── component.py (or main file)
        ├── tests/ (optional)
        └── README.md (optional)
        """
        issues = []
        warnings = []
        
        if not component_path.exists():
            return {
                "valid": False,
                "issues": ["Component path does not exist"],
                "warnings": []
            }
        
        # Check for __init__.py
        if not (component_path / "__init__.py").exists():
            issues.append("Missing __init__.py")
        
        # Check for main file
        main_files = list(component_path.glob("*.py"))
        if not main_files:
            issues.append("No Python files found")
        
        # Check for tests directory (optional but recommended)
        if not (component_path / "tests").exists():
            warnings.append("No tests/ directory (recommended)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_maat_compliance(code: str, file_path: Path) -> Dict[str, Any]:
        """
        Validate code follows Maat principles.
        
        Checks:
        - Truth: Proper validation, no false data
        - Balance: Efficient, no conflicts
        - Order: Consistent patterns
        - Justice: Proper access control
        - Self-Reflection: Logging, error handling
        """
        compliance = {
            "truth": [],
            "balance": [],
            "order": [],
            "justice": [],
            "self_reflection": []
        }
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error: {e}",
                "compliance": compliance
            }
        
        # Check for logging (Self-Reflection)
        has_logging = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "logging" in alias.name:
                        has_logging = True
            elif isinstance(node, ast.ImportFrom):
                if node.module and "logging" in node.module:
                    has_logging = True
        
        if has_logging:
            compliance["self_reflection"].append("✅ Logging imported")
        else:
            compliance["self_reflection"].append("⚠️  No logging found (recommended)")
        
        # Check for error handling (Self-Reflection)
        has_try_except = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                has_try_except = True
                break
        
        if has_try_except:
            compliance["self_reflection"].append("✅ Error handling present")
        else:
            compliance["self_reflection"].append("⚠️  No error handling found (recommended)")
        
        # Check for validation (Truth)
        has_validation = False
        validation_keywords = ["validate", "check", "verify", "assert"]
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if any(kw in node.name.lower() for kw in validation_keywords):
                    has_validation = True
                    break
        
        if has_validation:
            compliance["truth"].append("✅ Validation functions present")
        else:
            compliance["truth"].append("⚠️  No validation functions found (recommended)")
        
        # Check for docstrings (Order)
        has_docstrings = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    has_docstrings = True
                    break
        
        if has_docstrings:
            compliance["order"].append("✅ Docstrings present")
        else:
            compliance["order"].append("⚠️  No docstrings found (recommended)")
        
        return {
            "valid": True,
            "compliance": compliance
        }
    
    @staticmethod
    def check_conflicts(component_name: str, project_root: Path) -> Dict[str, Any]:
        """
        Check for naming conflicts with existing components.
        
        Returns:
            {
                "conflicts": List[str],
                "recommendations": List[str]
            }
        """
        conflicts = []
        recommendations = []
        
        # Check for duplicate directory
        component_dir = project_root / component_name
        if component_dir.exists():
            conflicts.append(f"Directory '{component_name}' already exists")
            recommendations.append(f"Use different name or merge with existing")
        
        # Check for duplicate Python module
        core_dir = project_root / "core"
        if core_dir.exists():
            for existing in core_dir.iterdir():
                if existing.is_dir() and existing.name == component_name:
                    conflicts.append(f"Component '{component_name}' already exists in core/")
                    recommendations.append(f"Use different name or extend existing component")
        
        return {
            "conflicts": conflicts,
            "recommendations": recommendations
        }
    
    @staticmethod
    def generate_component_template(component_name: str, component_type: str = "standard") -> Dict[str, str]:
        """
        Generate template code for new component following Maat standards.
        
        Args:
            component_name: Name of component
            component_type: "standard", "governance", "integration", "api"
        
        Returns:
            Dictionary with file paths and content
        """
        templates = {
            "standard": {
                "__init__.py": f'''"""
{component_name} - Maat-compliant component

Maat: Order - Consistent structure and patterns
"""

from .{component_name.lower()} import *

__all__ = []
''',
                f"{component_name.lower()}.py": f'''"""
{component_name} - Main component implementation

Maat Principles:
- Truth: Accurate data representation
- Balance: Efficient resource usage
- Order: Consistent structure
- Justice: Fair access control
- Self-Reflection: Proper logging and error handling
"""

import logging
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)


class {component_name}:
    """
    {component_name} component following Maat standards.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize {component_name}.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {{}}
        log.info(f"Initialized {{self.__class__.__name__}}")
    
    def validate(self) -> bool:
        """
        Validate component configuration.
        
        Maat: Truth - Ensure accurate configuration
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Add validation logic here
            return True
        except Exception as e:
            log.error(f"Validation failed: {{e}}")
            return False
'''
            },
            "governance": {
                "__init__.py": f'''"""
{component_name} - Maat governance component

Maat: Justice - Access control and policy enforcement
"""

from .{component_name.lower()} import *

__all__ = []
''',
                f"{component_name.lower()}.py": f'''"""
{component_name} - Governance component

Maat Principles:
- Truth: Accurate policy representation
- Balance: Fair access control
- Order: Consistent policy structure
- Justice: Proper enforcement
- Self-Reflection: Audit logging
"""

import logging
from typing import Dict, Any, Optional, List

log = logging.getLogger(__name__)


class {component_name}:
    """
    {component_name} governance component.
    """
    
    def __init__(self, policies: Optional[Dict[str, Any]] = None):
        """
        Initialize {component_name}.
        
        Args:
            policies: Optional policy dictionary
        """
        self.policies = policies or {{}}
        log.info(f"Initialized {{self.__class__.__name__}}")
    
    def validate_action(self, action: str, context: Dict[str, Any]) -> bool:
        """
        Validate action against policies.
        
        Maat: Justice - Fair access control
        
        Args:
            action: Action to validate
            context: Context information
        
        Returns:
            True if allowed, False otherwise
        """
        try:
            # Add validation logic here
            log.info(f"Validating action: {{action}}")
            return True
        except Exception as e:
            log.error(f"Validation failed: {{e}}")
            return False
    
    def audit_log(self, event: str, details: Dict[str, Any]):
        """
        Log audit event.
        
        Maat: Self-Reflection - System awareness
        
        Args:
            event: Event name
            details: Event details
        """
        log.info(f"Audit: {{event}} - {{details}}")
'''
            }
        }
        
        template = templates.get(component_type, templates["standard"])
        
        return template

