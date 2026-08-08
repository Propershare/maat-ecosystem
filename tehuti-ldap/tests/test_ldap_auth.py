#!/usr/bin/env python3
"""
LDAP Authentication Tests
Maat-Aligned Test Suite
"""

import unittest
from ldap3 import Server, Connection, ALL
import os


class TestLDAPAuth(unittest.TestCase):
    """Test LDAP authentication functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.ldap_host = os.getenv("LDAP_HOST", "127.0.0.1")
        cls.ldap_port = int(os.getenv("LDAP_PORT", "389"))
        cls.ldap_base = os.getenv("LDAP_BASE", "dc=tehuti,dc=lab")
        cls.ldap_admin = os.getenv("LDAP_ADMIN", "cn=admin,dc=tehuti,dc=lab")
        cls.ldap_password = os.getenv("LDAP_ADMIN_PASSWORD", "changeme")
        
        cls.server = Server(
            cls.ldap_host,
            port=cls.ldap_port,
            get_info=ALL
        )

    def test_server_connection(self):
        """Test LDAP server connection."""
        conn = Connection(self.server, auto_bind=True)
        self.assertTrue(conn.bound)
        conn.unbind()

    def test_admin_bind(self):
        """Test admin bind."""
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        self.assertTrue(conn.bound)
        conn.unbind()

    def test_search_base_dn(self):
        """Test searching base DN."""
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        result = conn.search(
            self.ldap_base,
            "(objectClass=*)",
            search_scope="BASE"
        )
        
        self.assertTrue(result)
        self.assertGreater(len(conn.entries), 0)
        conn.unbind()

    def test_search_users(self):
        """Test searching users."""
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        result = conn.search(
            f"ou=users,{self.ldap_base}",
            "(objectClass=maatUser)"
        )
        
        self.assertTrue(result)
        conn.unbind()

    def test_search_groups(self):
        """Test searching groups."""
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        result = conn.search(
            f"ou=groups,{self.ldap_base}",
            "(objectClass=maatGroup)"
        )
        
        self.assertTrue(result)
        conn.unbind()

    def test_user_authentication(self):
        """Test user authentication."""
        # This requires a test user to exist
        test_user = os.getenv("LDAP_TEST_USER", "imhotep")
        test_password = os.getenv("LDAP_TEST_PASSWORD", "changeme")
        
        conn = Connection(
            self.server,
            user=f"uid={test_user},ou=users,{self.ldap_base}",
            password=test_password,
            auto_bind=True
        )
        
        self.assertTrue(conn.bound)
        conn.unbind()


if __name__ == "__main__":
    unittest.main()

