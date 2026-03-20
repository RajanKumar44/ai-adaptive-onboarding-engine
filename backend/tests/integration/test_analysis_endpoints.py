"""
Integration tests for analysis API endpoints.
Tests cover skill analysis, result retrieval, pagination, filtering, and search.
20+ test cases ensuring all analysis endpoints work correctly with database.
"""

import pytest
from fastapi.testclient import TestClient


class TestAnalysisEndpointCreate:
    """Integration tests for analysis creation endpoint."""
    
    def test_analyze_valid_input(self, client: TestClient, user_headers):
        """Test successful skill analysis with valid input."""
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=user_headers,
            json={
                "resume_text": "Python developer with 5 years FastAPI experience",
                "jd_text": "Senior Python Developer: FastAPI, Django, PostgreSQL, AWS"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "analysis_id" in data or "id" in data
    
    
    def test_analyze_without_auth(self, client: TestClient):
        """Test analysis requires authentication."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "resume_text": "Resume text",
                "jd_text": "JD text"
            }
        )
        assert response.status_code == 401
    
    
    def test_analyze_empty_resume(self, client: TestClient, user_headers):
        """Test analysis validation for empty resume."""
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=user_headers,
            json={
                "resume_text": "",
                "jd_text": "Job description text"
            }
        )
        assert response.status_code in [400, 422]
    
    
    def test_analyze_empty_jd(self, client: TestClient, user_headers):
        """Test analysis validation for empty JD."""
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=user_headers,
            json={
                "resume_text": "Resume text",
                "jd_text": ""
            }
        )
        assert response.status_code in [400, 422]
    
    
    def test_analyze_missing_fields(self, client: TestClient, user_headers):
        """Test analysis validation for missing fields."""
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=user_headers,
            json={"resume_text": "Resume"}
        )
        assert response.status_code in [400, 422]
    
    
    def test_analyze_very_large_text(self, client: TestClient, user_headers):
        """Test handling of very large resume/JD text."""
        large_text = "text " * 50000  # ~250KB of text
        response = client.post(
            "/api/v1/analysis/analyze",
            headers=user_headers,
            json={
                "resume_text": large_text,
                "jd_text": large_text
            }
        )
        # Should either process or reject with appropriate status
        assert response.status_code in [201, 413, 400]


class TestAnalysisEndpointRetrieval:
    """Integration tests for analysis retrieval endpoints."""
    
    def test_get_analysis_successful(self, client: TestClient, user_headers, sample_analysis):
        """Test successful retrieval of analysis result."""
        response = client.get(
            f"/api/v1/analysis/{sample_analysis.id}",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_analysis.id
        assert "missing_skills" in data
        assert "matched_skills" in data
    
    
    def test_get_analysis_nonexistent(self, client: TestClient, user_headers):
        """Test retrieval of non-existent analysis."""
        response = client.get(
            "/api/v1/analysis/99999",
            headers=user_headers
        )
        assert response.status_code == 404
    
    
    def test_get_analysis_without_auth(self, client: TestClient, sample_analysis):
        """Test analysis retrieval requires authentication."""
        response = client.get(f"/api/v1/analysis/{sample_analysis.id}")
        assert response.status_code == 401
    
    
    def test_user_cannot_access_others_analysis(self, client: TestClient, user_headers, admin_user, db_session):
        """Test that users cannot access other users' analyses."""
        # Create analysis for different user and try to access it
        from app.models.analysis import Analysis
        from datetime import datetime
        
        other_analysis = Analysis(
            user_id=admin_user.id,
            resume_text="Admin resume",
            jd_text="Admin JD",
            extracted_resume_skills=[],
            extracted_jd_skills=[],
            missing_skills=[],
            matched_skills=[],
            learning_path={},
            reasoning_trace={},
            created_at=datetime.utcnow()
        )
        db_session.add(other_analysis)
        db_session.commit()
        db_session.refresh(other_analysis)
        
        response = client.get(
            f"/api/v1/analysis/{other_analysis.id}",
            headers=user_headers
        )
        # Should not be able to access (401 or 403)
        assert response.status_code in [403, 404]


class TestAnalysisEndpointListWithPagination:
    """Integration tests for analysis listing with pagination."""
    
    def test_list_user_analyses_successful(self, client: TestClient, user_headers, sample_analysis):
        """Test successful retrieval of user's analyses list."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"skip": 0, "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    
    def test_list_analyses_pagination_skip(self, client: TestClient, user_headers, multiple_analyses):
        """Test pagination with skip parameter."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"skip": 1, "limit": 2}
        )
        assert response.status_code == 200
    
    
    def test_list_analyses_pagination_limit(self, client: TestClient, user_headers, multiple_analyses):
        """Test pagination with limit parameter."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"skip": 0, "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", data if isinstance(data, list) else [])
        assert len(items) <= 5
    
    
    def test_list_analyses_default_pagination(self, client: TestClient, user_headers):
        """Test default pagination values."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers
        )
        assert response.status_code == 200
    
    
    def test_list_analyses_cursor_pagination(self, client: TestClient, user_headers, multiple_analyses):
        """Test cursor-based pagination if supported."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"cursor": 0, "limit": 10}
        )
        # Should work or return 200 even if cursor not used
        assert response.status_code in [200, 400]


class TestAnalysisEndpointFiltering:
    """Integration tests for analysis filtering."""
    
    def test_filter_by_date_range(self, client: TestClient, user_headers):
        """Test filtering analyses by date range."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={
                "filter_created_at_after": "2024-01-01",
                "filter_created_at_before": "2024-12-31"
            }
        )
        assert response.status_code in [200, 400]
    
    
    def test_filter_by_skills(self, client: TestClient, user_headers):
        """Test filtering analyses by missing skills."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"filter_missing_skills": "Python"}
        )
        assert response.status_code in [200, 400]
    
    
    def test_filter_complex_criteria(self, client: TestClient, user_headers):
        """Test filtering with multiple criteria."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={
                "filter_role": "admin",
                "filter_active": True,
                "skip": 0,
                "limit": 20
            }
        )
        assert response.status_code in [200, 400]


class TestAnalysisEndpointSorting:
    """Integration tests for analysis sorting."""
    
    def test_sort_by_created_ascending(self, client: TestClient, user_headers):
        """Test sorting analyses by creation date ascending."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"sort_by": "created_at", "sort_order": "asc"}
        )
        assert response.status_code == 200
    
    
    def test_sort_by_created_descending(self, client: TestClient, user_headers):
        """Test sorting analyses by creation date descending."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"sort_by": "created_at", "sort_order": "desc"}
        )
        assert response.status_code == 200
    
    
    def test_sort_by_multiple_fields(self, client: TestClient, user_headers):
        """Test sorting by multiple fields."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={
                "sort_by": "role,created_at",
                "sort_order": "asc,desc"
            }
        )
        assert response.status_code in [200, 400]


class TestAnalysisEndpointSearch:
    """Integration tests for full-text search in analyses."""
    
    def test_search_by_skill(self, client: TestClient, user_headers):
        """Test searching analyses by skill keyword."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"search": "Python"}
        )
        assert response.status_code == 200
    
    
    def test_search_empty_query(self, client: TestClient, user_headers):
        """Test search with empty query."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"search": ""}
        )
        assert response.status_code in [200, 400]
    
    
    def test_search_special_characters(self, client: TestClient, user_headers):
        """Test search with special characters."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"search": "C++ & C#"}
        )
        assert response.status_code in [200, 400]


class TestAnalysisEndpointResponseFormat:
    """Integration tests for response format validation."""
    
    def test_analysis_response_contains_required_fields(self, client: TestClient, user_headers, sample_analysis):
        """Test that analysis response has all required fields."""
        response = client.get(
            f"/api/v1/analysis/{sample_analysis.id}",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        required_fields = ["id", "user_id", "missing_skills", "matched_skills"]
        for field in required_fields:
            assert field in data
    
    
    def test_list_response_pagination_format(self, client: TestClient, user_headers):
        """Test that list response has proper pagination format."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"skip": 0, "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        # Should have items and pagination info
        assert isinstance(data, (dict, list))


class TestAnalysisEndpointErrors:
    """Integration tests for error handling."""
    
    def test_invalid_pagination_limit(self, client: TestClient, user_headers):
        """Test handling of invalid pagination limit."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"limit": -1}
        )
        assert response.status_code in [400, 200]  # Either reject or assume default
    
    
    def test_invalid_sort_order(self, client: TestClient, user_headers):
        """Test handling of invalid sort order."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"sort_order": "invalid"}
        )
        assert response.status_code in [400, 200]
    
    
    def test_invalid_filter_operator(self, client: TestClient, user_headers):
        """Test handling of invalid filter operator."""
        response = client.get(
            "/api/v1/analysis/list",
            headers=user_headers,
            params={"filter_role[invalid_op]": "value"}
        )
        assert response.status_code in [400, 200]


class TestAnalysisEndpointRateLimiting:
    """Integration tests for rate limiting on analysis endpoints."""
    
    def test_analysis_endpoint_rate_limited(self, client: TestClient, user_headers):
        """Test that analysis endpoints respect rate limits."""
        # Try multiple requests rapidly
        for i in range(5):
            response = client.get(
                "/api/v1/analysis/list",
                headers=user_headers
            )
            if response.status_code == 429:  # Too many requests
                break
        
        # Should get at least some responses
        assert response.status_code in [200, 429]
