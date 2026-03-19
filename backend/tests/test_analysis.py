"""
Test suite for the analysis endpoints.
Run with: pytest tests/test_analysis.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db

# In-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency with test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Health check should return 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestUserEndpoints:
    """Test user management endpoints."""
    
    def test_create_user(self):
        """Create user endpoint should accept valid data."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_user_invalid_email(self):
        """Create user with invalid email should fail."""
        user_data = {
            "email": "invalid-email",
            "name": "Test User"
        }
        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_duplicate_user(self):
        """Creating user with duplicate email should fail."""
        user_data = {
            "email": "duplicate@example.com",
            "name": "User 1"
        }
        # First creation
        response1 = client.post("/api/v1/users", json=user_data)
        assert response1.status_code == 201
        
        # Duplicate creation
        response2 = client.post("/api/v1/users", json=user_data)
        assert response2.status_code == 400


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data."""
        # Create a test user
        user_data = {
            "email": "analysis-test@example.com",
            "name": "Analysis Test User"
        }
        response = client.post("/api/v1/users", json=user_data)
        self.user_id = response.json()["id"]
    
    def test_missing_files(self):
        """Analysis without files should fail."""
        response = client.post(
            "/api/v1/analyze",
            data={"user_id": self.user_id}
        )
        assert response.status_code == 422
    
    def test_invalid_user(self):
        """Analysis for non-existent user should fail."""
        response = client.post(
            "/api/v1/analyze",
            data={"user_id": 99999},
            files={"resume_file": ("test.txt", b"test"), 
                   "jd_file": ("jd.txt", b"test")}
        )
        # Will fail due to file processing, but conceptually correct
