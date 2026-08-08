#!/usr/bin/env python3
"""
gitMaat LDAP Integration Tests
Maat-Aligned Test Suite
"""

import unittest
import sys
from pathlib import Path

# Add maatlangchain to path
workspace_root = None
current = Path(__file__).parent.parent.parent
for path in [current] + list(current.parents):
    if (path / "maatlangchain").exists():
        workspace_root = path
        break

if workspace_root:
    sys.path.insert(0, str(workspace_root / "maatlangchain"))
    from maat_memory import MaatMemory, get_unique_agent_id
    from maat_memory.ldap_integration import LDAPIntegration


class TestGitMaatLDAPIntegration(unittest.TestCase):
    """Test gitMaat LDAP integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        try:
            cls.memory = MaatMemory()
            cls.agent_id = get_unique_agent_id("test")
            cls.ldap_integration = LDAPIntegration(cls.memory)
        except Exception as e:
            cls.memory = None
            print(f"Warning: Could not initialize MaatMemory: {e}")

    def test_log_ldap_auth_success(self):
        """Test logging successful LDAP authentication."""
        if not self.memory:
            self.skipTest("MaatMemory not available")
        
        result = self.ldap_integration.log_ldap_auth(
            agent=self.agent_id,
            ldap_user="testuser",
            success=True,
            groups=["outer-ring"],
            metadata={"test": True}
        )
        
        self.assertIsNotNone(result)

    def test_log_ldap_auth_failure(self):
        """Test logging failed LDAP authentication."""
        if not self.memory:
            self.skipTest("MaatMemory not available")
        
        result = self.ldap_integration.log_ldap_auth(
            agent=self.agent_id,
            ldap_user="testuser",
            success=False,
            groups=[],
            metadata={"error": "test"}
        )
        
        self.assertIsNotNone(result)

    def test_map_ldap_to_agent(self):
        """Test mapping LDAP user to agent."""
        if not self.memory:
            self.skipTest("MaatMemory not available")
        
        self.ldap_integration.map_ldap_to_agent(
            ldap_user="testuser",
            agent_id=self.agent_id,
            metadata={"test": True}
        )
        
        # Verify mapping
        ldap_user = self.ldap_integration.get_ldap_user_from_agent(self.agent_id)
        self.assertEqual(ldap_user, "testuser")

    def test_get_ldap_user_groups(self):
        """Test getting LDAP user groups."""
        if not self.memory:
            self.skipTest("MaatMemory not available")
        
        # First log an auth event with groups
        self.ldap_integration.log_ldap_auth(
            agent=self.agent_id,
            ldap_user="testuser",
            success=True,
            groups=["outer-ring", "admins"]
        )
        
        # Get groups
        groups = self.ldap_integration.get_ldap_user_groups("testuser")
        self.assertIsInstance(groups, list)


if __name__ == "__main__":
    unittest.main()

