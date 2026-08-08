"""
Error Handling Tests for LDAP Server
Maat-Aligned Error Handling Testing
"""

import unittest
import ldap3
from ldap3 import Server, Connection, ALL
import os
import sys
import socket
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLDAPErrorHandling(unittest.TestCase):
    """Error handling tests for LDAP server"""
    
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
    
    def test_connection_failure(self):
        """Test handling of connection failures"""
        # Test connection to non-existent server
        invalid_server = Server('127.0.0.1:9999', get_info=ALL)
        
        with self.assertRaises(Exception):
            conn = Connection(
                invalid_server,
                user=self.ldap_admin,
                password=self.ldap_password,
                auto_bind=True
            )
    
    def test_authentication_failure(self):
        """Test handling of authentication failures"""
        server = Server(
            f'{self.ldap_host}:{self.ldap_port}',
            get_info=ALL
        )
        
        # Test with wrong password
        with self.assertRaises(ldap3.core.exceptions.LDAPInvalidCredentialsResult):
            conn = Connection(
                server,
                user=self.ldap_admin,
                password='wrongpassword',
                auto_bind=True
            )
        
        # Test with non-existent user
        with self.assertRaises(Exception):
            conn = Connection(
                server,
                user='cn=nonexistent,dc=tehuti,dc=lab',
                password='password',
                auto_bind=True
            )
    
    def test_query_errors(self):
        """Test handling of query errors"""
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
            # Test invalid search base
            with self.assertRaises(Exception):
                conn.search(
                    'ou=nonexistent,dc=tehuti,dc=lab',
                    '(objectClass=*)',
                    search_scope=ldap3.SUBTREE
                )
            
            # Test invalid filter
            with self.assertRaises(Exception):
                conn.search(
                    self.ldap_base,
                    'invalid(filter)',
                    search_scope=ldap3.SUBTREE
                )
        finally:
            conn.unbind()
    
    def test_database_errors(self):
        """Test handling of database errors"""
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
            # Test adding duplicate entry
            test_dn = f'uid=testduplicate,ou=users,{self.ldap_base}'
            
            # Add entry first time
            try:
                conn.add(
                    test_dn,
                    attributes={
                        'objectClass': ['inetOrgPerson', 'posixAccount', 'maatUser'],
                        'uid': 'testduplicate',
                        'cn': 'Test Duplicate',
                        'sn': 'Duplicate',
                        'mail': 'testduplicate@tehuti.lab',
                        'userPassword': 'TestPassword123!',
                        'homeDirectory': '/home/testduplicate',
                        'uidNumber': '9999',
                        'gidNumber': '9999'
                    }
                )
            except ldap3.core.exceptions.LDAPEntryAlreadyExistsResult:
                # Entry already exists, delete it first
                conn.delete(test_dn)
                conn.add(
                    test_dn,
                    attributes={
                        'objectClass': ['inetOrgPerson', 'posixAccount', 'maatUser'],
                        'uid': 'testduplicate',
                        'cn': 'Test Duplicate',
                        'sn': 'Duplicate',
                        'mail': 'testduplicate@tehuti.lab',
                        'userPassword': 'TestPassword123!',
                        'homeDirectory': '/home/testduplicate',
                        'uidNumber': '9999',
                        'gidNumber': '9999'
                    }
                )
            
            # Try to add again (should fail)
            with self.assertRaises(ldap3.core.exceptions.LDAPEntryAlreadyExistsResult):
                conn.add(
                    test_dn,
                    attributes={
                        'objectClass': ['inetOrgPerson', 'posixAccount', 'maatUser'],
                        'uid': 'testduplicate',
                        'cn': 'Test Duplicate',
                        'sn': 'Duplicate'
                    }
                )
            
            # Clean up
            try:
                conn.delete(test_dn)
            except:
                pass
                
        finally:
            conn.unbind()
    
    def test_network_timeout(self):
        """Test handling of network timeouts"""
        # Create server with very short timeout
        server = Server(
            f'{self.ldap_host}:{self.ldap_port}',
            get_info=ALL,
            connect_timeout=0.001  # Very short timeout
        )
        
        # Connection should timeout or fail quickly
        try:
            conn = Connection(
                server,
                user=self.ldap_admin,
                password=self.ldap_password,
                auto_bind=True,
                receive_timeout=0.001
            )
            # If connection succeeds, test query timeout
            try:
                conn.search(
                    self.ldap_base,
                    '(objectClass=*)',
                    search_scope=ldap3.SUBTREE
                )
            except Exception:
                # Timeout expected
                pass
            finally:
                conn.unbind()
        except Exception:
            # Timeout expected
            pass
    
    def test_connection_recovery(self):
        """Test recovery from connection errors"""
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
            # Perform initial operation
            result = conn.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=ldap3.BASE
            )
            self.assertTrue(result)
            
            # Simulate connection loss by unbinding
            conn.unbind()
            
            # Attempt to reconnect
            conn.rebind(
                user=self.ldap_admin,
                password=self.ldap_password
            )
            
            # Verify reconnection works
            result = conn.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=ldap3.BASE
            )
            self.assertTrue(result)
            
        finally:
            try:
                conn.unbind()
            except:
                pass


if __name__ == '__main__':
    unittest.main()

