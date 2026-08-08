"""
Performance Tests for LDAP Server
Maat-Aligned Performance Testing
"""

import unittest
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLDAPPerformance(unittest.TestCase):
    """Performance tests for LDAP server"""
    
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
    
    def test_concurrent_connections(self):
        """Test handling of concurrent connections"""
        num_threads = 10
        results = []
        
        def connect_and_search(thread_id):
            """Connect and perform search"""
            try:
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
                
                # Perform search
                result = conn.search(
                    self.ldap_base,
                    '(objectClass=*)',
                    search_scope=ldap3.BASE
                )
                
                conn.unbind()
                return {'thread_id': thread_id, 'success': result, 'error': None}
            except Exception as e:
                return {'thread_id': thread_id, 'success': False, 'error': str(e)}
        
        # Execute concurrent connections
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(connect_and_search, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all connections succeeded
        successful = sum(1 for r in results if r['success'])
        self.assertGreaterEqual(
            successful,
            num_threads * 0.8,  # At least 80% should succeed
            f"Only {successful}/{num_threads} concurrent connections succeeded"
        )
    
    def test_query_performance(self):
        """Test query performance benchmarks"""
        conn = Connection(
            self.server,
            user=self.ldap_admin,
            password=self.ldap_password,
            auto_bind=True
        )
        
        try:
            # Test 1: Base DN query
            start_time = time.time()
            result = conn.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=ldap3.BASE
            )
            base_query_time = time.time() - start_time
            
            self.assertTrue(result)
            self.assertLess(
                base_query_time,
                1.0,  # Should complete in under 1 second
                f"Base query took {base_query_time:.3f}s (expected < 1.0s)"
            )
            
            # Test 2: Subtree search
            start_time = time.time()
            result = conn.search(
                self.ldap_base,
                '(objectClass=*)',
                search_scope=SUBTREE,
                attributes=['uid', 'cn']
            )
            subtree_query_time = time.time() - start_time
            
            self.assertTrue(result)
            self.assertLess(
                subtree_query_time,
                2.0,  # Should complete in under 2 seconds
                f"Subtree query took {subtree_query_time:.3f}s (expected < 2.0s)"
            )
            
            # Test 3: Filtered search
            start_time = time.time()
            result = conn.search(
                f'ou=users,{self.ldap_base}',
                '(uid=*)',
                search_scope=SUBTREE,
                attributes=['uid']
            )
            filtered_query_time = time.time() - start_time
            
            self.assertTrue(result)
            self.assertLess(
                filtered_query_time,
                1.5,  # Should complete in under 1.5 seconds
                f"Filtered query took {filtered_query_time:.3f}s (expected < 1.5s)"
            )
            
        finally:
            conn.unbind()
    
    def test_load_testing(self):
        """Test server under load"""
        num_requests = 50
        results = []
        
        def perform_request(request_id):
            """Perform a single LDAP request"""
            try:
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
                
                start_time = time.time()
                result = conn.search(
                    self.ldap_base,
                    '(objectClass=*)',
                    search_scope=ldap3.BASE
                )
                elapsed = time.time() - start_time
                
                conn.unbind()
                return {
                    'request_id': request_id,
                    'success': result,
                    'elapsed': elapsed,
                    'error': None
                }
            except Exception as e:
                return {
                    'request_id': request_id,
                    'success': False,
                    'elapsed': 0,
                    'error': str(e)
                }
        
        # Execute load test
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_request, i) for i in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        total_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r['success'])
        failed = num_requests - successful
        avg_time = sum(r['elapsed'] for r in results) / len(results) if results else 0
        max_time = max((r['elapsed'] for r in results), default=0)
        
        # Verify performance metrics
        self.assertGreaterEqual(
            successful,
            num_requests * 0.9,  # At least 90% should succeed
            f"Only {successful}/{num_requests} requests succeeded"
        )
        
        self.assertLess(
            avg_time,
            0.5,  # Average response time should be under 500ms
            f"Average response time {avg_time:.3f}s is too high"
        )
        
        self.assertLess(
            max_time,
            2.0,  # Maximum response time should be under 2s
            f"Maximum response time {max_time:.3f}s is too high"
        )
        
        # Print performance summary
        print(f"\nLoad Test Results:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average response: {avg_time:.3f}s")
        print(f"  Max response: {max_time:.3f}s")
        print(f"  Requests/sec: {num_requests / total_time:.2f}")
    
    def test_connection_pooling(self):
        """Test connection pooling performance"""
        # Create multiple connections and reuse them
        connections = []
        
        try:
            # Create pool of connections
            pool_size = 5
            for i in range(pool_size):
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
                connections.append(conn)
            
            # Perform operations using pooled connections
            num_operations = 20
            start_time = time.time()
            
            for i in range(num_operations):
                conn = connections[i % pool_size]
                conn.search(
                    self.ldap_base,
                    '(objectClass=*)',
                    search_scope=ldap3.BASE
                )
            
            elapsed = time.time() - start_time
            avg_time = elapsed / num_operations
            
            self.assertLess(
                avg_time,
                0.2,  # Pooled connections should be faster
                f"Average pooled operation time {avg_time:.3f}s is too high"
            )
            
        finally:
            # Clean up connections
            for conn in connections:
                try:
                    conn.unbind()
                except:
                    pass


if __name__ == '__main__':
    unittest.main()

