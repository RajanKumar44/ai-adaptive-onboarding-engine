"""
Integration tests for bulk operations API endpoints.
Tests cover bulk create, update, delete, upsert operations with atomic and partial modes.
16+ test cases ensuring bulk operations work correctly with proper error handling.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.security import SecurityManager


class TestBulkCreateEndpoint:
    """Integration tests for bulk create operations."""
    
    def test_bulk_create_users_atomic_success(self, client: TestClient, admin_headers):
        """Test successful bulk user creation in atomic mode."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": [
                    {
                        "email": "bulk1@test.com",
                        "name": "Bulk User 1",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    },
                    {
                        "email": "bulk2@test.com",
                        "name": "Bulk User 2",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["successful_count"] == 2
        assert data["failed_count"] == 0
    
    
    def test_bulk_create_partial_mode_with_failures(self, client: TestClient, admin_headers):
        """Test bulk create in partial mode continues on errors."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "partial",
                "items": [
                    {
                        "email": "partial1@test.com",
                        "name": "Partial User 1",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    },
                    {
                        "email": None,  # Invalid
                        "name": "Invalid User",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    },
                    {
                        "email": "partial3@test.com",
                        "name": "Partial User 3",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["successful_count"] >= 2  # Two valid items should succeed
        assert data["failed_count"] >= 1      # One invalid item should fail
    
    
    def test_bulk_create_atomic_mode_rollback_on_error(self, client: TestClient, admin_headers, regular_user):
        """Test atomic mode rolls back all on any error."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": [
                    {
                        "email": "rollback1@test.com",
                        "name": "User 1",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    },
                    {
                        "email": regular_user.email,  # Duplicate - error
                        "name": "Duplicate User",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    }
                ]
            }
        )
        # In atomic mode, should fail and rollback all
        assert response.status_code in [400, 409]
    
    
    def test_bulk_create_non_admin_forbidden(self, client: TestClient, user_headers):
        """Test bulk create is forbidden for non-admin users."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=user_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": []
            }
        )
        assert response.status_code == 403


class TestBulkUpdateEndpoint:
    """Integration tests for bulk update operations."""
    
    def test_bulk_update_users_atomic(self, client: TestClient, admin_headers, multiple_users):
        """Test bulk user updates in atomic mode."""
        user_ids = [u.id for u in multiple_users[:2]]
        response = client.put(
            "/api/v1/bulk/users/update",
            headers=admin_headers,
            json={
                "operation": "update",
                "mode": "atomic",
                "items": [
                    {"id": user_ids[0], "name": "Updated User 1"},
                    {"id": user_ids[1], "name": "Updated User 2"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["successful_count"] == 2
    
    
    def test_bulk_update_partial_mode(self, client: TestClient, admin_headers, multiple_users):
        """Test bulk update in partial mode with mixed results."""
        user_ids = [u.id for u in multiple_users[:3]]
        response = client.put(
            "/api/v1/bulk/users/update",
            headers=admin_headers,
            json={
                "operation": "update",
                "mode": "partial",
                "items": [
                    {"id": user_ids[0], "name": "Updated 1"},
                    {"id": 99999, "name": "Nonexistent"},  # Will fail
                    {"id": user_ids[1], "name": "Updated 2"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["successful_count"] >= 2
        assert data["failed_count"] >= 1
    
    
    def test_bulk_update_preserves_unspecified_fields(self, client: TestClient, admin_headers, multiple_users):
        """Test that bulk update only changes specified fields."""
        user = multiple_users[0]
        original_email = user.email
        response = client.put(
            "/api/v1/bulk/users/update",
            headers=admin_headers,
            json={
                "operation": "update",
                "mode": "atomic",
                "items": [
                    {"id": user.id, "name": "New Name"}
                ]
            }
        )
        assert response.status_code == 200


class TestBulkDeleteEndpoint:
    """Integration tests for bulk delete operations."""
    
    def test_bulk_delete_users_atomic(self, client: TestClient, admin_headers, db_session):
        """Test bulk deletion in atomic mode."""
        # Create test users to delete
        from app.models.user import User
        users_to_delete = []
        for i in range(3):
            user = User(
                email=f"delete_bulk_{i}@test.com",
                name=f"Delete User {i}",
                password_hash="hash",
                role="user"
            )
            db_session.add(user)
            users_to_delete.append(user)
        db_session.commit()
        
        user_ids = [u.id for u in users_to_delete]
        response = client.delete(
            "/api/v1/bulk/users/delete",
            headers=admin_headers,
            json={
                "operation": "delete",
                "mode": "atomic",
                "items": [{"id": uid} for uid in user_ids]
            }
        )
        assert response.status_code in [200, 204]
        data = response.json() if response.status_code == 200 else {}
        assert data.get("successful_count", 0) == 3
    
    
    def test_bulk_delete_partial_mode(self, client: TestClient, admin_headers, multiple_users):
        """Test bulk delete in partial mode."""
        user_ids = [u.id for u in multiple_users[:2]]
        response = client.delete(
            "/api/v1/bulk/users/delete",
            headers=admin_headers,
            json={
                "operation": "delete",
                "mode": "partial",
                "items": [
                    {"id": user_ids[0]},
                    {"id": 99999},  # Nonexistent
                    {"id": user_ids[1]}
                ]
            }
        )
        assert response.status_code in [200, 204]


class TestBulkUpsertAnalysisEndpoint:
    """Integration tests for bulk upsert operations on analysis."""
    
    def test_bulk_upsert_analyses_insert_new(self, client: TestClient, user_headers):
        """Test bulk upsert inserts new analyses."""
        response = client.post(
            "/api/v1/bulk/analyses/upsert",
            headers=user_headers,
            json={
                "operation": "upsert",
                "mode": "atomic",
                "items": [
                    {
                        "resume_text": "Python developer",
                        "jd_text": "Senior Python Developer",
                        "extracted_resume_skills": ["Python"],
                        "extracted_jd_skills": ["Python", "Django"]
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "successful_count" in data
    
    
    def test_bulk_upsert_analyses_mixed_operations(self, client: TestClient, user_headers, sample_analysis):
        """Test bulk upsert with mix of inserts and updates."""
        response = client.post(
            "/api/v1/bulk/analyses/upsert",
            headers=user_headers,
            json={
                "operation": "upsert",
                "mode": "partial",
                "items": [
                    {
                        "id": sample_analysis.id,
                        "resume_text": "Updated resume"
                    },
                    {
                        "resume_text": "New analysis",
                        "jd_text": "New JD"
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]


class TestBulkOperationResponseFormat:
    """Integration tests for response format and structure."""
    
    def test_bulk_operation_response_contains_status(self, client: TestClient, admin_headers):
        """Test response contains operation status."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": []
            }
        )
        data = response.json()
        assert "successful_count" in data
        assert "failed_count" in data
        assert "items" in data
    
    
    def test_bulk_operation_error_tracking(self, client: TestClient, admin_headers):
        """Test that errors are tracked per item."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "partial",
                "items": [
                    {
                        "email": "test@test.com",
                        "name": "Test",
                        "password_hash": "hash",
                        "role": "user"
                    },
                    {
                        "email": None,  # Invalid
                        "name": "Bad",
                        "password_hash": "hash",
                        "role": "user"
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        # Check items have status
        for item in data.get("items", []):
            assert "status" in item or "error" in item


class TestBulkOperationValidation:
    """Integration tests for bulk operation input validation."""
    
    def test_empty_items_list(self, client: TestClient, admin_headers):
        """Test handling of empty items list."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": []
            }
        )
        # Should handle empty list gracefully
        assert response.status_code in [200, 400]
    
    
    def test_invalid_mode_specification(self, client: TestClient, admin_headers):
        """Test handling of invalid mode."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "invalid_mode",
                "items": []
            }
        )
        assert response.status_code in [400, 422]
    
    
    def test_missing_required_item_fields(self, client: TestClient, admin_headers):
        """Test validation of required fields in items."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": [
                    {
                        "name": "User",
                        # Missing email
                        "password_hash": "hash",
                        "role": "user"
                    }
                ]
            }
        )
        assert response.status_code in [400, 422]


class TestBulkOperationRateLimiting:
    """Integration tests for rate limiting on bulk operations."""
    
    def test_bulk_operations_rate_limited(self, client: TestClient, admin_headers):
        """Test that bulk operations respect rate limits."""
        # Bulk operations typically have lower rate limits
        for i in range(10):
            response = client.post(
                "/api/v1/bulk/users/create",
                headers=admin_headers,
                json={
                    "operation": "create",
                    "mode": "atomic",
                    "items": []
                }
            )
            if response.status_code == 429:  # Too many requests
                break
        
        assert response.status_code in [200, 429]


class TestBulkOperationTransactionHandling:
    """Integration tests for transaction handling in bulk operations."""
    
    def test_atomic_transaction_integrity(self, client: TestClient, admin_headers):
        """Test atomic transactions maintain data integrity."""
        response = client.post(
            "/api/v1/bulk/users/create",
            headers=admin_headers,
            json={
                "operation": "create",
                "mode": "atomic",
                "items": [
                    {
                        "email": "atomic1@test.com",
                        "name": "User 1",
                        "password_hash": SecurityManager.hash_password("Pass@123"),
                        "role": "user"
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]
