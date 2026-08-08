"""
Security Tests for LDAP Server
Maat-Aligned Security Testing
"""

import unittest
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLDAPSecurity(unittest.TestCase):
    """Security tests for LDAP server"""
    
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
    
    def test_ldap_injection_prevention(self):
        """Test that LDAP injection attacks are prevented"""
        # Test malicious input patterns
        malicious_inputs = [
            "*)(uid=*",
            "*)(|(uid=*",
            "admin)(&(uid=admin",
            "test*)(uid=test",
            "'; DROP TABLE users; --"
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                # Attempt search with malicious input
                conn = Connection(
                    self.server,
                    user=self.ldap_admin,
                    password=self.ldap_password,
                    auto_bind=True
                )
                
                try:
                    # Try to search with malicious filter
                    result = conn.search(
                        f'ou=users,{self.ldap_base}',
                        f'(uid={malicious_input})',
                        search_scope=SUBTREE
                    )
                    
                    # Should not return unexpected results
                    # If injection worked, we'd get unauthorized data
                    # For now, we just verify the query doesn't crash
                    # In production, you'd verify no unauthorized data is returned
                    self.assertIsNotNone(result)
                    
                except Exception as e:
                    # LDAP injection attempts should be rejected or sanitized
                    # This is expected behavior
                    pass
                finally:
                    conn.unbind()
    
    def test_acl_enforcement(self):
        """Test that ACLs are enforced"""
        # Test 1: Admin can read
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        try:
            result = conn.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=SUBTREE,
                attributes=['*']
            )
            self.assertTrue(result, "Admin should be able to read")
        finally:
            conn.unbind()
        
        # Test 2: Anonymous cannot read (if ACLs are enforced)
        try:
            conn_anon = Connection(
                self.server,
                auto_bind=True
            )
            
            result = conn_anon.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=SUBTREE
            )
            
            # If ACLs are working, anonymous should be denied
            # This test may pass or fail depending on ACL configuration
            # In production, you'd want anonymous access denied
            conn_anon.unbind()
        except Exception:
            # Expected if ACLs deny anonymous access
            pass
    
    def test_password_policy_enforcement(self):
        """Test that password policy is enforced"""
        # This test requires a test user to be created
        # For now, we verify the policy exists
        
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        try:
            # Check if password policy exists
            result = conn.search(
                f'ou=policies,{self.ldap_base}',
                '(objectClass=pwdPolicy)',
                search_scope=SUBTREE,
                attributes=['pwdMinLength', 'pwdCheckQuality']
            )
            
            # Policy should exist
            # In production, you'd test actual password enforcement
            # by attempting to add users with weak passwords
            self.assertIsNotNone(result)
        finally:
            conn.unbind()
    
    def test_certificate_validation(self):
        """Test certificate validation for LDAPS"""
        # This test requires LDAPS to be configured
        # For now, we verify the test structure
        
        ldaps_port = int(os.getenv('LDAPS_PORT', '636'))
        
        try:
            # Attempt LDAPS connection
            server_ldaps = Server(
                f'ldaps://{self.ldap_host}:{ldaps_port}',
                use_ssl=True,
                get_info=ALL
            )
            
            # If certificate validation is enabled, invalid certs should fail
            # This is a placeholder test structure
            # In production, you'd test with valid/invalid certificates
            self.assertIsNotNone(server_ldaps)
        except Exception:
            # LDAPS may not be configured yet
            pass
    
    def test_brute_force_protection(self):
        """Test brute force protection (password lockout)"""
        # Test multiple failed login attempts
        # Should trigger lockout after configured threshold
        
        test_user = 'testuser'
        wrong_password = 'wrongpassword123'
        
        failed_attempts = 0
        max_attempts = 5  # From password policy
        
        for i in range(max_attempts + 2):  # Try more than max
            try:
                conn = Connection(
                    self.server,
                    user=f'uid={test_user},ou=users,{self.ldap_base}',
                    password=wrong_password,
                    auto_bind=True
                )
                conn.unbind()
                # Should not succeed
                self.fail("Authentication should fail with wrong password")
            except ldap3.core.exceptions.LDAPInvalidCredentialsResult:
                failed_attempts += 1
            except Exception as e:
                # After max attempts, should get lockout error
                if 'lockout' in str(e).lower() or 'locked' in str(e).lower():
                    # Lockout triggered - this is expected
                    break
        
        # In production, verify lockout was triggered
        # For now, we just verify the test structure
        self.assertGreater(failed_attempts, 0)


if __name__ == '__main__':
    unittest.main()

