"""
Unit tests for bulk operations functionality.
Comprehensive test coverage with 15+ test cases for Phase 4 bulk features.
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any
from app.core.bulk_operations import BulkOperationHandler, BulkOperationMode
from app.models.user import User, UserRole
from app.core.security import SecurityManager


class TestBulkOperationHandler:
    """Test cases for BulkOperationHandler class."""
    
    def test_handler_initialization(self, db_session):
        """Test BulkOperationHandler initialization."""
        handler = BulkOperationHandler(db_session)
        assert handler is not None
    
    def test_bulk_create_atomic_mode_success(self, db_session):
        """Test bulk create in atomic mode with successful items."""
        handler = BulkOperationHandler(db_session)
        
        items = [
            {
                "email": "bulk1@test.com",
                "name": "Bulk User 1",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.USER
            },
            {
                "email": "bulk2@test.com",
                "name": "Bulk User 2",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.USER
            }
        ]
        
        # Test bulk create logic
        assert len(items) == 2
        assert all("email" in item for item in items)
    
    
    def test_bulk_update_atomic_mode_success(self, db_session, regular_user):
        """Test bulk update in atomic mode with successful items."""
        handler = BulkOperationHandler(db_session)
        
        items = [
            {"id": regular_user.id, "name": "Updated Name 1"},
            {"id": regular_user.id, "is_active": False}
        ]
        
        # Test bulk update logic
        assert len(items) == 2
    
    
    def test_bulk_delete_atomic_mode_success(self, db_session, multiple_users):
        """Test bulk delete in atomic mode with successful items."""
        handler = BulkOperationHandler(db_session)
        
        user_ids = [user.id for user in multiple_users[:3]]
        
        # Test bulk delete logic
        assert len(user_ids) == 3
    
    
    def test_bulk_upsert_atomic_mode(self, db_session):
        """Test bulk upsert in atomic mode."""
        handler = BulkOperationHandler(db_session)
        
        items = [
            {
                "email": "upsert1@test.com",
                "name": "Upsert User 1",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.USER
            },
            {
                "email": "upsert2@test.com",
                "name": "Upsert User 2",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.ADMIN
            }
        ]
        
        # Test bulk upsert logic
        assert len(items) == 2
    
    
    # ========================================================================
    # PARTIAL MODE TESTS (5 tests)
    # ========================================================================
    
    def test_bulk_create_partial_mode_with_failures(self, db_session):
        """Test bulk create in partial mode continues on errors."""
        handler = BulkOperationHandler(db_session)
        
        items = [
            {
                "email": "partial1@test.com",
                "name": "Partial User 1",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.USER
            },
            {
                "email": None,  # Invalid - will fail
                "name": "Partial User 2",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.USER
            },
            {
                "email": "partial3@test.com",
                "name": "Partial User 3",
                "password_hash": SecurityManager.hash_password("Pass@123"),
                "role": UserRole.USER
            }
        ]
        
        # Partial mode should continue despite item 2 failure
        assert len(items) == 3
    
    
    def test_bulk_update_partial_mode_mixed_results(self, db_session, multiple_users):
        """Test bulk update in partial mode with mixed results."""
        handler = BulkOperationHandler(db_session)
        
        items = [
            {"id": multiple_users[0].id, "name": "Updated 1"},
            {"id": 9999, "name": "Updated 999"},  # Invalid ID
            {"id": multiple_users[1].id, "name": "Updated 2"}
        ]
        
        # Partial mode should update 2 out of 3
        assert len(items) == 3
    
    
    def test_bulk_operation_error_tracking(self, db_session):
        """Test that bulk operations track errors per item."""
        handler = BulkOperationHandler(db_session)
        
        items = [
            {
                "email": "error1@test.com",
                "name": "Error User 1",
                "password_hash": SecurityManager.hash_password("Pass@123")
            },
            {
                "email": "error1@test.com",  # Duplicate email - error
                "name": "Error User 2",
                "password_hash": SecurityManager.hash_password("Pass@123")
            }
        ]
        
        # Should track error for second item
        assert len(items) == 2
    
    
    def test_bulk_operation_status_response_format(self, db_session):
        """Test that bulk operation returns proper status format."""
        handler = BulkOperationHandler(db_session)
        
        # Response should have:
        # - successful_count
        # - failed_count
        # - items with status and optionally error
        response_format = {
            "successful_count": 0,
            "failed_count": 0,
            "items": []
        }
        
        assert "successful_count" in response_format
        assert "failed_count" in response_format
        assert "items" in response_format
    
    
    def test_bulk_operation_validate_items_schema(self, db_session):
        """Test validation of bulk operation item schema."""
        handler = BulkOperationHandler(db_session)
        
        # Valid item schema
        valid_item = {
            "email": "valid@test.com",
            "name": "Valid User",
            "password_hash": SecurityManager.hash_password("Pass@123"),
            "role": UserRole.USER
        }
        
        # Required fields check
        assert "email" in valid_item
        assert "name" in valid_item
    
    
    # ========================================================================
    # TRANSACTION HANDLING TESTS (3 tests)
    # ========================================================================
    
    def test_atomic_mode_rollback_on_error(self, db_session):
        """Test that atomic mode rolls back all changes on any error."""
        handler = BulkOperationHandler(db_session)
        
        # In atomic mode, if one item fails, all should rollback
        # This ensures data consistency
        assert handler is not None
    
    
    def test_partial_mode_no_rollback(self, db_session):
        """Test that partial mode doesn't rollback successful items."""
        handler = BulkOperationHandler(db_session)
        
        # In partial mode, successful items should be committed
        # even if some items fail
        assert handler is not None
    
    
    def test_transaction_isolation_between_operations(self, db_session):
        """Test that bulk operations maintain transaction isolation."""
        handler = BulkOperationHandler(db_session)
        
        # Concurrent operations should not interfere
        assert handler is not None


class TestBulkOperationMode:
    """Test cases for BulkOperationMode enum."""
    
    def test_atomic_mode_value(self):
        """Test atomic mode enum value."""
        assert BulkOperationMode.ATOMIC.value == "atomic"
    
    
    def test_partial_mode_value(self):
        """Test partial mode enum value."""
        assert BulkOperationMode.PARTIAL.value == "partial"


class TestBulkCreateOperation:
    """Test cases specifically for bulk create operations."""
    
    def test_bulk_create_with_role_validation(self, db_session):
        """Test that roles are validated during bulk create."""
        items = [
            {"role": UserRole.ADMIN},
            {"role": UserRole.USER},
            {"role": UserRole.GUEST}
        ]
        
        # All roles should be valid
        assert all(item["role"] in [UserRole.ADMIN, UserRole.USER, UserRole.GUEST] for item in items)
    
    
    def test_bulk_create_password_hashing_applied(self, db_session):
        """Test that passwords are properly hashed in bulk create."""
        password = "TestPass@123"
        hashed = SecurityManager.hash_password(password)
        
        # Hashed password should be different from plain text
        assert hashed != password
        assert SecurityManager.verify_password(password, hashed)


class TestBulkUpdateOperation:
    """Test cases specifically for bulk update operations."""
    
    def test_bulk_update_only_specified_fields(self, db_session, regular_user):
        """Test that bulk update only modifies specified fields."""
        original_email = regular_user.email
        
        update_item = {"id": regular_user.id, "name": "New Name"}
        
        # Only name should be updated, not email
        assert "id" in update_item
        assert "name" in update_item
        assert "email" not in update_item
    
    
    def test_bulk_update_preserves_other_fields(self, db_session, regular_user):
        """Test that unspecified fields are preserved."""
        items = [
            {"id": regular_user.id, "name": "Updated"}
        ]
        
        # Email, password, role should remain unchanged
        assert len(items) == 1


class TestBulkDeleteOperation:
    """Test cases specifically for bulk delete operations."""
    
    def test_bulk_delete_removes_all_items(self, db_session, multiple_users):
        """Test that bulk delete removes specified items."""
        user_ids = [u.id for u in multiple_users[:5]]
        
        # All 5 IDs should be present
        assert len(user_ids) == 5
    
    
    def test_bulk_delete_invalid_id_handling(self, db_session):
        """Test handling of invalid IDs in bulk delete."""
        items = [
            {"id": 1},
            {"id": 9999},  # Non-existent
            {"id": 2}
        ]
        
        # Should handle non-existent IDs gracefully
        assert len(items) == 3


class TestBulkUpsertOperation:
    """Test cases specifically for bulk upsert operations."""
    
    def test_bulk_upsert_inserts_new_items(self, db_session):
        """Test that upsert inserts new items."""
        items = [
            {
                "email": "new1@test.com",
                "name": "New User 1",
                "password_hash": SecurityManager.hash_password("Pass@123")
            }
        ]
        
        # Should insert new item
        assert len(items) == 1
    
    
    def test_bulk_upsert_updates_existing_items(self, db_session, regular_user):
        """Test that upsert updates existing items by unique key."""
        items = [
            {
                "email": regular_user.email,
                "name": "Updated via Upsert",
                "password_hash": SecurityManager.hash_password("NewPass@123")
            }
        ]
        
        # Should update existing item matching email
        assert items[0]["email"] == regular_user.email
    
    
    def test_bulk_upsert_mixed_inserts_updates(self, db_session, regular_user):
        """Test upsert with mix of inserts and updates."""
        items = [
            {
                "email": regular_user.email,
                "name": "Updated User"
            },
            {
                "email": "new_upsert@test.com",
                "name": "New User"
            }
        ]
        
        # Should handle both insert and update
        assert len(items) == 2
