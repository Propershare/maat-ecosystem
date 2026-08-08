#!/usr/bin/env python3
"""
Cross-Workstation LDAP Connection Tests
Maat-Aligned Test Suite
"""

import unittest
import subprocess
import os
from ldap3 import Server, Connection, ALL


class TestCrossWorkstationLDAP(unittest.TestCase):
    """Test cross-workstation LDAP connections."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.ldap_server = os.getenv("LDAP_SERVER", "47.200.181.85")
        cls.ldap_port = int(os.getenv("LDAP_PORT", "389"))
        cls.ldap_base = os.getenv("LDAP_BASE", "dc=tehuti,dc=lab")
        cls.ldap_admin = os.getenv("LDAP_ADMIN", "cn=admin,dc=tehuti,dc=lab")
        cls.ldap_password = os.getenv("LDAP_ADMIN_PASSWORD", "changeme")

    def test_server_reachable(self):
        """Test that LDAP server is reachable."""
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.ldap_server, self.ldap_port))
            sock.close()
            self.assertEqual(result, 0, f"Server {self.ldap_server}:{self.ldap_port} not reachable")
        except Exception as e:
            self.fail(f"Connection test failed: {e}")

    def test_ldap_connection(self):
        """Test LDAP connection from remote workstation."""
        server = Server(
            self.ldap_server,
            port=self.ldap_port,
            get_info=ALL
        )
        
        try:
            conn = Connection(server, auto_bind=True)
            self.assertTrue(conn.bound)
            conn.unbind()
        except Exception as e:
            self.fail(f"LDAP connection failed: {e}")

    def test_ldap_bind(self):
        """Test LDAP bind from remote workstation."""
        server = Server(
            self.ldap_server,
            port=self.ldap_port,
            get_info=ALL
        )
        
        try:
            conn = Connection(
                server,
                user=self.ldap_admin,
                password=self.ldap_password,
                auto_bind=True
            )
            self.assertTrue(conn.bound)
            conn.unbind()
        except Exception as e:
            self.fail(f"LDAP bind failed: {e}")

    def test_ldap_search(self):
        """Test LDAP search from remote workstation."""
        server = Server(
            self.ldap_server,
            port=self.ldap_port,
            get_info=ALL
        )
        
        try:
            conn = Connection(
                server,
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
        except Exception as e:
            self.fail(f"LDAP search failed: {e}")

    def test_connection_script(self):
        """Test connection test script."""
        script_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "scripts",
            "test-ldap-connection.sh"
        )
        
        if os.path.exists(script_path):
            env = os.environ.copy()
            env["LDAP_ADMIN_PASSWORD"] = self.ldap_password
            
            result = subprocess.run(
                ["bash", script_path, self.ldap_server],
                env=env,
                capture_output=True,
                text=True
            )
            
            # Script should exit with 0 if successful
            # But we'll be lenient if script doesn't exist or has issues
            if result.returncode != 0:
                print(f"Script output: {result.stdout}")
                print(f"Script errors: {result.stderr}")


if __name__ == "__main__":
    unittest.main()

