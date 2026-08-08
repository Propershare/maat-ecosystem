#!/usr/bin/env python3
"""
TehutiGuard LDAP Integration Tests
Maat-Aligned Test Suite
"""

import unittest
import sys
from pathlib import Path

# Add tehuti-guard to path
workspace_root = None
current = Path(__file__).parent.parent.parent
for path in [current] + list(current.parents):
    if (path / "tehuti-guard").exists():
        workspace_root = path
        break

if workspace_root:
    sys.path.insert(0, str(workspace_root / "tehuti-guard" / "src"))


class TestTehutiGuardLDAPIntegration(unittest.TestCase):
    """Test TehutiGuard LDAP integration."""

    def test_get_maat_role_from_groups(self):
        """Test getting Maat role from LDAP groups."""
        try:
            from ldap_policy import getMaatRoleFromLDAPGroups
            
            # Test outer-ring
            role = getMaatRoleFromLDAPGroups(["outer-ring"])
            self.assertEqual(role, "outer-ring")
            
            # Test middle-ring
            role = getMaatRoleFromLDAPGroups(["middle-ring"])
            self.assertEqual(role, "middle-ring")
            
            # Test inner-ring
            role = getMaatRoleFromLDAPGroups(["inner-ring"])
            self.assertEqual(role, "inner-ring")
            
            # Test priority (outer > middle > inner)
            role = getMaatRoleFromLDAPGroups(["inner-ring", "outer-ring"])
            self.assertEqual(role, "outer-ring")
            
        except ImportError:
            self.skipTest("TehutiGuard not available")

    def test_get_permissions_for_role(self):
        """Test getting permissions for Maat role."""
        try:
            from ldap_policy import getPermissionsForMaatRole
            
            # Test outer-ring permissions
            perms = getPermissionsForMaatRole("outer-ring")
            self.assertTrue(perms["read"])
            self.assertTrue(perms["write"])
            self.assertTrue(perms["execute"])
            self.assertTrue(perms["propose"])
            
            # Test middle-ring permissions
            perms = getPermissionsForMaatRole("middle-ring")
            self.assertTrue(perms["read"])
            self.assertFalse(perms["write"])
            self.assertFalse(perms["execute"])
            self.assertTrue(perms["propose"])
            
            # Test inner-ring permissions
            perms = getPermissionsForMaatRole("inner-ring")
            self.assertTrue(perms["read"])
            self.assertFalse(perms["write"])
            self.assertFalse(perms["execute"])
            self.assertFalse(perms["propose"])
            
        except ImportError:
            self.skipTest("TehutiGuard not available")

    def test_enforce_ldap_policy(self):
        """Test enforcing LDAP policy."""
        try:
            from ldap_policy import enforceLDAPPolicy
            
            # Test write action for outer-ring
            decision = enforceLDAPPolicy(
                {
                    "action": "write",
                    "resource": "maatlangchain/",
                    "user": "testuser"
                },
                {
                    "uid": "testuser",
                    "groups": ["outer-ring"]
                }
            )
            
            self.assertTrue(decision["allowed"])
            self.assertEqual(decision["maatRole"], "outer-ring")
            
            # Test write action for inner-ring (should be denied)
            decision = enforceLDAPPolicy(
                {
                    "action": "write",
                    "resource": "maatlangchain/",
                    "user": "testuser"
                },
                {
                    "uid": "testuser",
                    "groups": ["inner-ring"]
                }
            )
            
            self.assertFalse(decision["allowed"])
            
        except ImportError:
            self.skipTest("TehutiGuard not available")


if __name__ == "__main__":
    unittest.main()

