"""
Performance and load tests for the API.
Tests cover concurrent requests, response times, and system behavior under load.
12+ test cases ensuring acceptable performance metrics.
"""

import pytest
import time
import concurrent.futures
from fastapi.testclient import TestClient
from typing import List


class TestAPIResponseTimes:
    """Tests for API response time performance."""
    
    def test_auth_login_response_time(self, client: TestClient, regular_user):
        """Test login endpoint responds within acceptable time."""
        start = time.time()
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@test.com",
                "password": "UserPass@123"
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second
    
    
    def test_list_users_response_time(self, client: TestClient, admin_headers):
        """Test user listing responds within acceptable time."""
        start = time.time()
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={"skip": 0, "limit": 50}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond in under 2 seconds
    
    
    def test_analysis_response_time(self, client: TestClient, user_headers):
        """Test analysis endpoint responds within acceptable time."""
        start = time.time()
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=user_headers,
            json={
                "resume_text": "Python developer",
                "jd_text": "Python role"
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code in [200, 201]
        assert elapsed < 5.0  # Analysis can take longer
    
    
    def test_search_response_time(self, client: TestClient, user_headers):
        """Test search endpoint responds within acceptable time."""
        start = time.time()
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"search": "Python", "limit": 50}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0


class TestConcurrentRequests:
    """Tests for API behavior with concurrent requests."""
    
    def test_concurrent_login_requests(self, client: TestClient):
        """Test handling of concurrent login requests."""
        def login_user(client_obj):
            return client_obj.post(
                "/api/v1/auth/login",
                json={
                    "email": "user@test.com",
                    "password": "UserPass@123"
                }
            )
        
        # Simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(login_user, client) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert len(results) == 5
        assert all(r.status_code == 200 for r in results)
    
    
    def test_concurrent_analysis_requests(self, client: TestClient, user_headers):
        """Test handling of concurrent analysis requests."""
        def run_analysis(client_obj, headers):
            return client_obj.post(
                "/api/v1/analysis/analyze",
                headers=headers,
                json={
                    "resume_text": "Python developer",
                    "jd_text": "Python role"
                }
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_analysis, client, user_headers) for _ in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Should handle concurrent requests
        assert len(results) == 3
        assert all(r.status_code in [200, 201] for r in results)
    
    
    def test_concurrent_bulk_operations(self, client: TestClient, admin_headers):
        """Test handling of concurrent bulk operations."""
        from app.core.security import SecurityManager
        
        def bulk_create(client_obj, headers, index):
            return client_obj.post(
                "/api/v1/bulk/users/create",
                headers=headers,
                json={
                    "operation": "create",
                    "mode": "atomic",
                    "items": [
                        {
                            "email": f"concurrent_user_{index}_{i}@test.com",
                            "name": f"User {index}_{i}",
                            "password_hash": SecurityManager.hash_password("Pass@123"),
                            "role": "user"
                        }
                        for i in range(2)
                    ]
                }
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(bulk_create, client, admin_headers, i) for i in range(2)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert len(results) == 2


class TestPaginationPerformance:
    """Tests for pagination performance with large datasets."""
    
    def test_pagination_with_skip_limit_performance(self, client: TestClient, admin_headers):
        """Test pagination performance with offset/limit."""
        start = time.time()
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={"skip": 0, "limit": 100}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should handle large limits efficiently
        assert elapsed < 3.0
    
    
    def test_pagination_deep_offset_performance(self, client: TestClient, admin_headers):
        """Test pagination with large offset values."""
        start = time.time()
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={"skip": 1000, "limit": 50}
        )
        elapsed = time.time() - start
        
        # Even with large offset, should respond quickly
        assert elapsed < 3.0
    
    
    def test_cursor_pagination_performance(self, client: TestClient, admin_headers):
        """Test cursor-based pagination performance."""
        start = time.time()
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={"cursor": 0, "limit": 50}
        )
        elapsed = time.time() - start
        
        # Cursor pagination should be consistent
        assert elapsed < 2.0


class TestSearchPerformance:
    """Tests for full-text search performance."""
    
    def test_simple_search_performance(self, client: TestClient, user_headers):
        """Test simple search response time."""
        start = time.time()
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"search": "Python"}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0
    
    
    def test_complex_search_performance(self, client: TestClient, user_headers):
        """Test complex search with filters."""
        start = time.time()
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={
                "search": "Python",
                "filter_role": "admin",
                "sort_by": "created_at",
                "sort_order": "desc",
                "skip": 0,
                "limit": 20
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code in [200, 400]
        # Complex queries might be slower
        assert elapsed < 3.0


class TestDatabaseQueryPerformance:
    """Tests for database query performance."""
    
    def test_filtered_query_performance(self, client: TestClient, admin_headers):
        """Test performance of filtered database queries."""
        start = time.time()
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={
                "filter_role": "admin",
                "filter_active": True,
                "skip": 0,
                "limit": 50
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code in [200, 400]
        assert elapsed < 2.0
    
    
    def test_sorted_query_performance(self, client: TestClient, admin_headers):
        """Test performance of sorted queries."""
        start = time.time()
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={
                "sort_by": "created_at",
                "sort_order": "desc",
                "skip": 0,
                "limit": 50
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0


class TestBulkOperationPerformance:
    """Tests for bulk operation performance."""
    
    def test_bulk_create_performance(self, client: TestClient, admin_headers):
        """Test bulk create operation performance."""
        from app.core.security import SecurityManager
        
        start = time.time()
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": [
                    {
                        "email": f"perf_bulk_{i}@test.com",
                        "name": f"Perf User {i}",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    }
                    for i in range(10)
                ]
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code in [200, 201]
        # Bulk operations should complete in reasonable time
        assert elapsed < 5.0
    
    
    def test_bulk_update_performance(self, client: TestClient, admin_headers, multiple_users):
        """Test bulk update operation performance."""
        user_ids = [u.id for u in multiple_users[:5]]
        
        start = time.time()
        response = client.put(
            "/api/v1/bulk/users/update",
            headers=admin_headers,
            json={
                "operation": "update",
                "mode": "atomic",
                "items": [
                    {"id": uid, "name": f"Updated User {i}"}
                    for i, uid in enumerate(user_ids)
                ]
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 3.0


class TestMemoryUsage:
    """Tests for memory efficiency."""
    
    def test_large_response_handling(self, client: TestClient, admin_headers):
        """Test handling of large responses."""
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={"skip": 0, "limit": 1000}  # Large limit
        )
        
        # Should handle large response
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            # Should have valid JSON
            assert isinstance(response.json(), (dict, list))


class TestRateLimitingPerformance:
    """Tests for rate limiting behavior."""
    
    def test_rate_limit_response_time(self, client: TestClient, user_headers):
        """Test that rate limiting doesn't significantly impact response time."""
        response_times = []
        
        for i in range(5):
            start = time.time()
            response = client.get(
                "/api/v1/analysis/list",
                headers=user_headers
            )
            elapsed = time.time() - start
            response_times.append(elapsed)
        
        # Average response time should be consistent
        avg_time = sum(response_times) / len(response_times)
        assert avg_time < 2.0


class TestEndpointStressTest:
    """Stress tests for API endpoints."""
    
    def test_rapid_successive_requests(self, client: TestClient, user_headers):
        """Test API handles rapid successive requests."""
        success_count = 0
        rate_limited_count = 0
        
        for i in range(20):
            response = client.get(
                "/api/v1/analysis/list",
                headers=user_headers
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
        
        # Should handle most requests
        assert success_count > 10 or rate_limited_count > 5
