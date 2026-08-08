"""
Integration Tests for LDAP Server
Maat-Aligned Integration Testing
"""

import unittest
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
import os
import sys
from pathlib import Path

# Add maatlangchain to path for gitMaat imports
workspace_root = None
current = Path(__file__).parent.parent.parent
for path in [current] + list(current.parents):
    if (path / "maatlangchain").exists():
        workspace_root = path
        break

if workspace_root:
    sys.path.insert(0, str(workspace_root / "maatlangchain"))
    try:
        from maat_memory import MaatMemory, get_unique_agent_id
        from maat_memory.ldap_integration import LDAPIntegration
        GITMAAT_AVAILABLE = True
    except ImportError:
        GITMAAT_AVAILABLE = False
else:
    GITMAAT_AVAILABLE = False

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLDAPIntegration(unittest.TestCase):
    """Integration tests for LDAP server"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.ldap_host = os.getenv('LDAP_HOST', '127.0.0.1')
        cls.ldap_port = int(os.getenv('LDAP_PORT', '389'))
        cls.ldap_base = os.getenv('LDAP_BASE', 'dc=tehuti,dc=lab')
        cls.ldap_admin = os.getenv('LDAP_ADMIN', 'cn=admin,dc=tehuti,dc=lab')
        
        # Get password from secure file
        password_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.ldap_admin_password'
        )
        if os.path.exists(password_file):
            with open(password_file, 'r') as f:
                cls.ldap_password = f.read().strip()
        else:
            cls.ldap_password = os.getenv('LDAP_ADMIN_PASSWORD', 'changeme')
        
        cls.server = Server(
            f'{cls.ldap_host}:{cls.ldap_port}',
            get_info=ALL
        )
        
        # Initialize gitMaat if available
        if GITMAAT_AVAILABLE:
            cls.agent_id = get_unique_agent_id("test")
            cls.memory = MaatMemory()
            cls.ldap_integration = LDAPIntegration(cls.memory)
        else:
            cls.memory = None
            cls.ldap_integration = None
    
    def test_end_to_end_authentication_flow(self):
        """Test complete authentication flow"""
        # Step 1: Connect to LDAP
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        try:
            # Step 2: Search for a test user
            test_user = 'testuser'
            result = conn.search(
                f'ou=users,{self.ldap_base}',
                f'(uid={test_user})',
                search_scope=SUBTREE,
                attributes=['uid', 'mail', 'memberOf']
            )
            
            if result and len(conn.entries) > 0:
                # Step 3: Authenticate as test user
                user_dn = conn.entries[0].entry_dn
                user_password = 'TestPassword123!'  # Should be from secure storage
                
                # Test authentication
                test_conn = Connection(
                    self.server,
                    user=user_dn,
                    password=user_password,
                    auto_bind=True
                )
                
                # Authentication successful
                self.assertTrue(test_conn.bound)
                test_conn.unbind()
            else:
                # User doesn't exist, skip test
                self.skipTest(f"Test user {test_user} not found")
                
        finally:
            conn.unbind()
    
    @unittest.skipUnless(GITMAAT_AVAILABLE, "gitMaat not available")
    def test_gitmaat_logging_integration(self):
        """Test gitMaat logging integration"""
        if not self.ldap_integration:
            self.skipTest("LDAP integration not available")
        
        # Test user
        test_ldap_user = 'testuser'
        test_agent_id = f"test_{test_ldap_user}"
        
        # Log LDAP authentication event
        audit_id = self.ldap_integration.log_ldap_auth(
            agent=test_agent_id,
            ldap_user=test_ldap_user,
            success=True,
            groups=['outer-ring'],
            metadata={
                'email': f'{test_ldap_user}@tehuti.lab',
                'test': True
            }
        )
        
        self.assertIsNotNone(audit_id)
        
        # Verify audit trail entry
        audit_entries = self.memory.get_audit_trail(
            action='ldap_auth_success',
            resource=f'ldap_user:{test_ldap_user}',
            limit=1
        )
        
        self.assertGreater(len(audit_entries), 0)
        self.assertEqual(audit_entries[0]['metadata']['ldap_user'], test_ldap_user)
    
    @unittest.skipUnless(GITMAAT_AVAILABLE, "gitMaat not available")
    def test_ldap_user_to_agent_mapping(self):
        """Test mapping LDAP users to agents"""
        if not self.ldap_integration:
            self.skipTest("LDAP integration not available")
        
        # Test user
        test_ldap_user = 'testuser'
        test_agent_id = f"test_{test_ldap_user}"
        
        # Map LDAP user to agent
        self.ldap_integration.map_ldap_to_agent(
            ldap_user=test_ldap_user,
            agent_id=test_agent_id,
            metadata={
                'email': f'{test_ldap_user}@tehuti.lab',
                'test': True
            }
        )
        
        # Retrieve mapping
        mapped_user = self.ldap_integration.get_ldap_user_from_agent(test_agent_id)
        self.assertEqual(mapped_user, test_ldap_user)
    
    @unittest.skipUnless(GITMAAT_AVAILABLE, "gitMaat not available")
    def test_ldap_user_groups_retrieval(self):
        """Test retrieving LDAP user groups from gitMaat"""
        if not self.ldap_integration:
            self.skipTest("LDAP integration not available")
        
        # Test user
        test_ldap_user = 'testuser'
        test_agent_id = f"test_{test_ldap_user}"
        test_groups = ['outer-ring', 'admins']
        
        # Log authentication with groups
        self.ldap_integration.log_ldap_auth(
            agent=test_agent_id,
            ldap_user=test_ldap_user,
            success=True,
            groups=test_groups,
            metadata={
                'email': f'{test_ldap_user}@tehuti.lab'
            }
        )
        
        # Retrieve groups
        groups = self.ldap_integration.get_ldap_user_groups(test_ldap_user)
        
        # Verify groups match
        self.assertEqual(set(groups), set(test_groups))
    
    def test_cross_workstation_scenario(self):
        """Test cross-workstation LDAP connection scenario"""
        # This test simulates a connection from another workstation
        # In production, you'd test actual network connections
        
        # Test connection from different host perspective
        server = Server(
            f'{self.ldap_host}:{self.ldap_port}',
            get_info=ALL
        )
        
        conn = Connection(
            server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        try:
            # Verify connection works
            result = conn.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=ldap3.BASE
            )
            self.assertTrue(result)
            
            # In production, you'd also test:
            # - LDAPS connection (port 636)
            # - Certificate validation
            # - Network latency
            # - Connection pooling
            
        finally:
            conn.unbind()
    
    @unittest.skipUnless(GITMAAT_AVAILABLE, "gitMaat not available")
    def test_tehuti_guard_policy_enforcement(self):
        """Test TehutiGuard policy enforcement with LDAP"""
        # This test requires TehutiGuard to be available
        # For now, we test the LDAP group retrieval that TehutiGuard would use
        
        if not self.ldap_integration:
            self.skipTest("LDAP integration not available")
        
        # Test user with outer-ring group
        test_ldap_user = 'testuser'
        test_groups = ['outer-ring']
        
        # Log authentication
        self.ldap_integration.log_ldap_auth(
            agent='test_agent',
            ldap_user=test_ldap_user,
            success=True,
            groups=test_groups
        )
        
        # Retrieve groups (as TehutiGuard would)
        groups = self.ldap_integration.get_ldap_user_groups(test_ldap_user)
        
        # Verify groups are correct
        self.assertIn('outer-ring', groups)
        
        # In production, you'd test:
        # - Policy enforcement based on groups
        # - Access control decisions
        # - Three-ring governance


if __name__ == '__main__':
    unittest.main()

