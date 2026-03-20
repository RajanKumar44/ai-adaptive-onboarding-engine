"""
Pytest configuration and fixtures for the entire test suite.
Provides database fixtures, client fixtures, mock data, and authentication fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, UserRole
from app.models.analysis import Analysis
from app.core.security import SecurityManager
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
import json


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def db_engine():
    """
    Create in-memory SQLite database for testing.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create database session for each test.
    Rollback after test to ensure clean state.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    Create FastAPI test client with test database session.
    """
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        name="Admin User",
        password_hash=SecurityManager.hash_password("AdminPass@123"),
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session: Session) -> User:
    """Create a regular user for testing."""
    user = User(
        email="user@test.com",
        name="Test User",
        password_hash=SecurityManager.hash_password("UserPass@123"),
        role=UserRole.USER,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def guest_user(db_session: Session) -> User:
    """Create a guest user for testing."""
    user = User(
        email="guest@test.com",
        name="Guest User",
        password_hash=SecurityManager.hash_password("GuestPass@123"),
        role=UserRole.GUEST,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session: Session) -> User:
    """Create an inactive user for testing."""
    user = User(
        email="inactive@test.com",
        name="Inactive User",
        password_hash=SecurityManager.hash_password("InactivePass@123"),
        role=UserRole.USER,
        is_active=False,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def multiple_users(db_session: Session) -> list:
    """Create multiple users for bulk operation testing."""
    users = []
    for i in range(10):
        user = User(
            email=f"user{i}@test.com",
            name=f"User {i}",
            password_hash=SecurityManager.hash_password(f"Pass@123{i}"),
            role=UserRole.USER if i % 2 == 0 else UserRole.ADMIN,
            is_active=i % 3 != 0,  # Some inactive
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(user)
        users.append(user)
    db_session.commit()
    return users


# ============================================================================
# ANALYSIS FIXTURES
# ============================================================================

@pytest.fixture
def sample_analysis(db_session: Session, regular_user: User) -> Analysis:
    """Create a sample analysis for testing."""
    analysis = Analysis(
        user_id=regular_user.id,
        resume_text="Python Developer with 5 years experience in FastAPI and Django",
        jd_text="Senior Python Developer: FastAPI, Django, PostgreSQL, AWS, Docker",
        extracted_resume_skills=["Python", "FastAPI", "Django", "PostgreSQL"],
        extracted_jd_skills=["Python", "FastAPI", "Django", "PostgreSQL", "AWS", "Docker"],
        missing_skills=["AWS", "Docker"],
        matched_skills=["Python", "FastAPI", "Django", "PostgreSQL"],
        learning_path={
            "AWS": {"duration": "3 months", "priority": "high"},
            "Docker": {"duration": "2 weeks", "priority": "high"}
        },
        reasoning_trace={
            "AWS": "Required for job but not in resume",
            "Docker": "Required for job but not in resume"
        },
        created_at=datetime.utcnow()
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)
    return analysis


@pytest.fixture
def multiple_analyses(db_session: Session, regular_user: User) -> list:
    """Create multiple analyses for bulk testing."""
    analyses = []
    skills_list = [
        {"resume": ["Python", "Django"], "jd": ["Python", "Django", "PostgreSQL"]},
        {"resume": ["JavaScript", "React"], "jd": ["JavaScript", "React", "Node.js"]},
        {"resume": ["Java", "Spring"], "jd": ["Java", "Spring", "Kafka"]},
    ]
    
    for i, skills in enumerate(skills_list):
        analysis = Analysis(
            user_id=regular_user.id,
            resume_text=f"Resume {i}",
            jd_text=f"JD {i}",
            extracted_resume_skills=skills["resume"],
            extracted_jd_skills=skills["jd"],
            missing_skills=[s for s in skills["jd"] if s not in skills["resume"]],
            matched_skills=[s for s in skills["resume"] if s in skills["jd"]],
            learning_path={},
            reasoning_trace={},
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(analysis)
        analyses.append(analysis)
    
    db_session.commit()
    return analyses


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    """Get JWT token for admin user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass@123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient, regular_user: User) -> str:
    """Get JWT token for regular user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "UserPass@123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def guest_token(client: TestClient, guest_user: User) -> str:
    """Get JWT token for guest user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "guest@test.com", "password": "GuestPass@123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Get authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token: str) -> Dict[str, str]:
    """Get authorization headers with regular user token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def guest_headers(guest_token: str) -> Dict[str, str]:
    """Get authorization headers with guest token."""
    return {"Authorization": f"Bearer {guest_token}"}


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def mock_skill_extraction() -> Dict[str, Any]:
    """
    Mock data for skill extraction testing.
    """
    return {
        "resume_skills": ["Python", "FastAPI", "Django", "PostgreSQL", "AWS"],
        "jd_skills": ["Python", "FastAPI", "Django", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
        "matched_skills": ["Python", "FastAPI", "Django", "PostgreSQL", "AWS"],
        "missing_skills": ["Docker", "Kubernetes"],
        "total_match_percentage": 71.43  # 5 out of 7
    }


@pytest.fixture
def mock_learning_path() -> Dict[str, Any]:
    """
    Mock data for learning path generation.
    """
    return {
        "skills": {
            "Docker": {
                "duration_hours": 40,
                "priority": "high",
                "resources": [
                    {"title": "Docker Official Guide", "type": "documentation"},
                    {"title": "Docker Deep Dive", "type": "course"}
                ]
            },
            "Kubernetes": {
                "duration_hours": 80,
                "priority": "medium",
                "resources": [
                    {"title": "Kubernetes in Action", "type": "book"},
                    {"title": "CKA Preparation", "type": "course"}
                ]
            }
        },
        "estimated_total_hours": 120
    }


@pytest.fixture
def bulk_create_payload() -> Dict[str, Any]:
    """Payload for bulk create operations."""
    return {
        "operation": "create",
        "items": [
            {
                "email": "bulk1@test.com",
                "name": "Bulk User 1",
                "password_hash": SecurityManager.hash_password("BulkPass@123"),
                "role": "user"
            },
            {
                "email": "bulk2@test.com",
                "name": "Bulk User 2",
                "password_hash": SecurityManager.hash_password("BulkPass@123"),
                "role": "user"
            }
        ],
        "atomic": True
    }


@pytest.fixture
def bulk_update_payload(regular_user: User) -> Dict[str, Any]:
    """Payload for bulk update operations."""
    return {
        "operation": "update",
        "items": [
            {"id": regular_user.id, "name": "Updated User 1"},
            {"id": regular_user.id, "role": "admin"}
        ],
        "atomic": True
    }


# ============================================================================
# PAGINATION & FILTERING FIXTURES
# ============================================================================

@pytest.fixture
def pagination_params() -> Dict[str, int]:
    """Standard pagination parameters."""
    return {"skip": 0, "limit": 10}


@pytest.fixture
def sort_params() -> Dict[str, str]:
    """Standard sort parameters."""
    return {"sort_by": "created_at", "sort_order": "desc"}


@pytest.fixture
def filter_params() -> Dict[str, Any]:
    """Standard filter parameters."""
    return {"filter_role": "admin", "filter_active": True}


@pytest.fixture
def search_params() -> Dict[str, str]:
    """Standard search parameters."""
    return {"search": "python"}


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def valid_password() -> str:
    """Valid password for testing."""
    return "ValidPass@123"


@pytest.fixture
def invalid_passwords() -> list:
    """List of invalid passwords for validation testing."""
    return [
        "short",              # Too short
        "nouppercase@123",   # No uppercase
        "NOLOWERCASE@123",   # No lowercase
        "NoSpecialChar123",  # No special characters
        "NoDigits@abc",      # No digits
    ]


@pytest.fixture
def valid_emails() -> list:
    """Valid email addresses for testing."""
    return [
        "user@example.com",
        "test.user@example.co.uk",
        "user+tag@example.com",
    ]


@pytest.fixture
def invalid_emails() -> list:
    """Invalid email addresses for testing."""
    return [
        "invalid.email",
        "@example.com",
        "user@",
        "user name@example.com",
        "",
    ]
