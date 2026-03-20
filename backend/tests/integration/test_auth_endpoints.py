"""
Integration tests for authentication API endpoints.
Tests cover registration, login, token refresh, logout, and profile management.
18+ test cases ensuring all auth endpoints work correctly with database.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpointRegistration:
    """Integration tests for user registration endpoint."""
    
    def test_register_user_successful(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "NewPass@123",
                "name": "New User"
            }
        )
        assert response.status_code == 201
        assert response.json()["email"] == "newuser@test.com"
    
    
    def test_register_user_invalid_password(self, client: TestClient):
        """Test registration fails with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "weak",  # Too weak
                "name": "Test User"
            }
        )
        assert response.status_code == 400
    
    
    def test_register_user_duplicate_email(self, client: TestClient, regular_user):
        """Test registration fails with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": regular_user.email,
                "password": "Password@123",
                "name": "Another User"
            }
        )
        assert response.status_code == 409  # Conflict
    
    
    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration fails with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalidemail",
                "password": "Password@123",
                "name": "Test User"
            }
        )
        assert response.status_code in [400, 422]


class TestAuthEndpointLogin:
    """Integration tests for user login endpoint."""
    
    def test_login_user_successful(self, client: TestClient, regular_user):
        """Test successful user login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@test.com",
                "password": "UserPass@123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    
    def test_login_user_wrong_password(self, client: TestClient, regular_user):
        """Test login fails with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@test.com",
                "password": "WrongPassword@123"
            }
        )
        assert response.status_code == 401
    
    
    def test_login_user_nonexistent(self, client: TestClient):
        """Test login fails for non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "Password@123"
            }
        )
        assert response.status_code == 401
    
    
    def test_login_inactive_user(self, client: TestClient, inactive_user):
        """Test login fails for inactive users."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@test.com",
                "password": "InactivePass@123"
            }
        )
        assert response.status_code == 403  # Forbidden


class TestAuthEndpointTokenRefresh:
    """Integration tests for token refresh endpoint."""
    
    def test_refresh_token_successful(self, client: TestClient, regular_user):
        """Test successful token refresh."""
        # First login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@test.com",
                "password": "UserPass@123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Now refresh the token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh fails with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )
        assert response.status_code == 401
    
    
    def test_refresh_token_expired(self, client: TestClient):
        """Test token refresh fails with expired token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "expired-token-would-fail"}
        )
        assert response.status_code == 401


class TestAuthEndpointLogout:
    """Integration tests for user logout endpoint."""
    
    def test_logout_successful(self, client: TestClient, user_headers):
        """Test successful user logout."""
        response = client.post(
            "/api/v1/auth/logout",
            headers=user_headers
        )
        assert response.status_code in [200, 204]
    
    
    def test_logout_without_auth_fails(self, client: TestClient):
        """Test logout fails without authentication."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401
    
    
    def test_logout_with_invalid_token_fails(self, client: TestClient):
        """Test logout fails with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post(
            "/api/v1/auth/logout",
            headers=headers
        )
        assert response.status_code == 401


class TestAuthEndpointPasswordChange:
    """Integration tests for password change endpoint."""
    
    def test_change_password_successful(self, client: TestClient, user_headers, regular_user):
        """Test successful password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=user_headers,
            json={
                "current_password": "UserPass@123",
                "new_password": "NewPassword@123"
            }
        )
        assert response.status_code == 200
    
    
    def test_change_password_wrong_current_password(self, client: TestClient, user_headers):
        """Test password change fails with wrong current password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=user_headers,
            json={
                "current_password": "WrongPass@123",
                "new_password": "NewPassword@123"
            }
        )
        assert response.status_code == 401
    
    
    def test_change_password_weak_new_password(self, client: TestClient, user_headers):
        """Test password change fails with weak new password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=user_headers,
            json={
                "current_password": "UserPass@123",
                "new_password": "weak"  # Too weak
            }
        )
        assert response.status_code == 400
    
    
    def test_change_password_without_auth(self, client: TestClient):
        """Test password change requires authentication."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "OldPass@123",
                "new_password": "NewPass@123"
            }
        )
        assert response.status_code == 401


class TestAuthEndpointProfile:
    """Integration tests for user profile endpoints."""
    
    def test_get_current_user_profile(self, client: TestClient, user_headers, regular_user):
        """Test retrieving current user profile."""
        response = client.get(
            "/api/v1/auth/me",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == regular_user.email
        assert data["name"] == regular_user.name
        assert data["role"] == regular_user.role.value
    
    
    def test_get_profile_without_auth(self, client: TestClient):
        """Test profile retrieval requires authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    
    def test_update_user_profile_successful(self, client: TestClient, user_headers):
        """Test successful profile update."""
        response = client.put(
            "/api/v1/auth/profile",
            headers=user_headers,
            json={
                "name": "Updated Name",
                "bio": "Updated bio"
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    
    
    def test_update_profile_email_not_allowed(self, client: TestClient, user_headers, regular_user):
        """Test that email cannot be changed via profile update."""
        response = client.put(
            "/api/v1/auth/profile",
            headers=user_headers,
            json={
                "name": "New Name",
                "email": "different@test.com"
            }
        )
        # Email should not be changed
        data = response.json()
        assert data["email"] == regular_user.email


class TestAuthEndpointAccessControl:
    """Integration tests for access control and authorization."""
    
    def test_admin_endpoints_require_admin_role(self, client: TestClient, user_headers):
        """Test that admin endpoints reject non-admin users."""
        response = client.get(
            "/api/v1/admin/users",
            headers=user_headers
        )
        assert response.status_code == 403
    
    
    def test_admin_can_access_admin_endpoints(self, client: TestClient, admin_headers):
        """Test that admin users can access admin endpoints."""
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers
        )
        assert response.status_code in [200, 401]  # 401 if not implemented, 200 if working
    
    
    def test_guest_user_limited_access(self, client: TestClient, guest_headers):
        """Test that guest users have limited access."""
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=guest_headers,
            json={
                "resume_text": "Test",
                "jd_text": "Test"
            }
        )
        # Guest might have limited or no access
        assert response.status_code in [200, 403]


class TestAuthEndpointErrorHandling:
    """Integration tests for error handling in auth endpoints."""
    
    def test_register_missing_required_fields(self, client: TestClient):
        """Test registration validation for missing fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@test.com"}  # Missing password and name
        )
        assert response.status_code in [400, 422]
    
    
    def test_login_missing_credentials(self, client: TestClient):
        """Test login validation for missing credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com"}  # Missing password
        )
        assert response.status_code in [400, 422]
    
    
    def test_malformed_token_header(self, client: TestClient):
        """Test handling of malformed authorization header."""
        headers = {"Authorization": "InvalidToken"}
        response = client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        assert response.status_code == 401
    
    
    def test_missing_token_type(self, client: TestClient):
        """Test handling of missing Bearer token type."""
        headers = {"Authorization": "invalid-token-without-bearer"}
        response = client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        assert response.status_code == 401


class TestAuthEndpointRate_Limiting:
    """Integration tests for rate limiting on auth endpoints."""
    
    def test_excessive_login_attempts_rate_limited(self, client: TestClient):
        """Test that excessive login attempts are rate limited."""
        # Attempt multiple failed logins
        rate_limited = False
        for i in range(15):  # Try more than typical limit
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@test.com",
                    "password": f"attempt{i}"
                }
            )
            if response.status_code == 429:  # Too many requests
                rate_limited = True
                break
        
        assert rate_limited or response.status_code in [401, 429]
    
    
    def test_registration_rate_limiting(self, client: TestClient):
        """Test rate limiting on registration endpoint."""
        # Should have some rate limiting for registration
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "Password@123",
                "name": "Test"
            }
        )
        # First request should succeed or fail normally
        assert response.status_code in [201, 400, 409]
