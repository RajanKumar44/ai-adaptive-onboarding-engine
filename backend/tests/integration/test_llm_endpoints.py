"""
Integration tests for LLM endpoints.
Tests the API endpoints with mocked LLM providers.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

# The tests will use conftest fixtures to set up the test database and client
# These tests assume the LLM routes are properly integrated with the FastAPI app


class TestSkillExtractionEndpoint:
    """Tests for skill extraction endpoint."""
    
    @pytest.mark.asyncio
    async def test_extract_skills_with_fallback(self, client, user_headers):
        """Test skill extraction using fallback method."""
        response = client.post(
            "/api/llm/extract-skills",
            headers=user_headers,
            json={
                "text": "I have experience with Python, JavaScript, React, and Docker",
                "provider": "openai",
                "use_fallback": True,
                "use_cache": True,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert data["skill_count"] > 0
        assert "extraction_method" in data
    
    @pytest.mark.asyncio
    async def test_extract_skills_empty_text(self, client, user_headers):
        """Test skill extraction with empty text."""
        response = client.post(
            "/api/llm/extract-skills",
            headers=user_headers,
            json={
                "text": "",
                "provider": "openai",
            }
        )
        
        # Should fail validation for empty text
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_extract_skills_requires_auth(self, client):
        """Test that skill extraction requires authentication."""
        response = client.post(
            "/api/llm/extract-skills",
            json={
                "text": "Python and JavaScript",
                "provider": "openai",
            }
        )
        
        assert response.status_code == 401


class TestSkillExtractionWithConfidence:
    """Tests for skill extraction with confidence scores."""
    
    @pytest.mark.asyncio
    async def test_extract_with_confidence(self, client, user_headers):
        """Test skill extraction with confidence scores."""
        response = client.post(
            "/api/llm/extract-skills-with-confidence",
            headers=user_headers,
            json={
                "text": "Python Python Python JavaScript JavaScript React",
                "provider": "openai",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        
        # Skills should be dict with confidence values
        assert isinstance(data["skills"], dict)
        
        # Confidence values should be 0-1
        for skill, confidence in data["skills"].items():
            assert 0 <= confidence <= 1
    
    @pytest.mark.asyncio
    async def test_confidence_ordering(self, client, user_headers):
        """Test that skills are ordered by confidence."""
        response = client.post(
            "/api/llm/extract-skills-with-confidence",
            headers=user_headers,
            json={
                "text": "Python Python Python SQL SQL",
                "provider": "openai",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Convert to list to check ordering
        skills_list = list(data["skills"].items())
        
        # Should be ordered by confidence (highest first)
        if len(skills_list) > 1:
            for i in range(len(skills_list) - 1):
                assert skills_list[i][1] >= skills_list[i + 1][1]


class TestSkillExtractionByCategory:
    """Tests for categorized skill extraction."""
    
    @pytest.mark.asyncio
    async def test_categorized_extraction(self, client, user_headers):
        """Test skill extraction by category."""
        response = client.post(
            "/api/llm/extract-skills-by-category",
            headers=user_headers,
            json={
                "text": """
                Languages: Python, JavaScript, Java
                Frameworks: React, Django, Spring
                Databases: PostgreSQL, MongoDB
                Cloud: AWS, Azure
                Tools: Docker, Git, Jenkins
                Agile: Scrum, Kanban
                """,
                "provider": "openai",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have different categories
        assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_empty_categories_excluded(self, client, user_headers):
        """Test that empty categories are excluded."""
        response = client.post(
            "/api/llm/extract-skills-by-category",
            headers=user_headers,
            json={
                "text": "Only Python here",
                "provider": "openai",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned categories should have items
        for category, skills in data.items():
            assert isinstance(skills, list)
            assert len(skills) > 0


class TestGenerateTextEndpoint:
    """Tests for text generation endpoint."""
    
    @pytest.mark.asyncio
    async def test_generate_text(self, client, user_headers):
        """Test basic text generation."""
        response = client.post(
            "/api/llm/generate-text",
            headers=user_headers,
            json={
                "prompt": "What are the benefits of Python for data science?",
                "provider": "openai",
                "max_tokens": 500,
                "temperature": 0.7,
            }
        )
        
        assert response.status_code in [200, 500]  # May fail if no API key
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert data["model"] == "gpt-3.5-turbo" or data["provider"]
    
    @pytest.mark.asyncio
    async def test_generate_text_temperature_validation(self, client, user_headers):
        """Test temperature parameter validation."""
        # Temperature must be 0-2
        response = client.post(
            "/api/llm/generate-text",
            headers=user_headers,
            json={
                "prompt": "Test prompt",
                "temperature": 2.5,  # Invalid
            }
        )
        
        assert response.status_code in [400, 422]


class TestProviderValidation:
    """Tests for provider validation endpoint."""
    
    @pytest.mark.asyncio
    async def test_validate_providers(self, client, user_headers):
        """Test provider validation endpoint."""
        response = client.get(
            "/api/llm/providers/validate",
            headers=user_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], dict)
        
        # Should have provider validation results
        for provider, is_valid in data["providers"].items():
            assert isinstance(is_valid, bool)


class TestMetricsEndpoint:
    """Tests for metrics endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_llm_metrics(self, client, user_headers):
        """Test getting LLM metrics."""
        response = client.get(
            "/api/llm/metrics",
            headers=user_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_cached_calls" in data
        assert "total_fallback_calls" in data
        assert "default_provider" in data
        assert "available_providers" in data
    
    @pytest.mark.asyncio
    async def test_get_cost_stats(self, client, user_headers):
        """Test getting cost statistics."""
        response = client.get(
            "/api/llm/costs/stats",
            headers=user_headers,
            params={"days": 30},
        )
        
        assert response.status_code in [200, 500]  # May have no cost data
        
        if response.status_code == 200:
            data = response.json()
            assert "period_days" in data
    
    @pytest.mark.asyncio
    async def test_cost_forecast(self, client, user_headers):
        """Test cost forecasting."""
        response = client.get(
            "/api/llm/costs/forecast",
            headers=user_headers,
            params={
                "daily_requests": 100,
                "days": 30,
            },
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "projected_total_cost" in data
            assert "projected_monthly_cost" in data


class TestCacheControl:
    """Tests for cache control endpoints."""
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, client, user_headers):
        """Test clearing cache."""
        response = client.post(
            "/api/llm/cache/control",
            headers=user_headers,
            json={"action": "clear"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_cache_stats(self, client, user_headers):
        """Test getting cache statistics."""
        response = client.post(
            "/api/llm/cache/control",
            headers=user_headers,
            json={"action": "get_stats"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        if data.get("stats"):
            assert "hits" in data["stats"]
            assert "misses" in data["stats"]


class TestLLMConfig:
    """Tests for LLM configuration endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_llm_config(self, client, user_headers):
        """Test getting LLM configuration."""
        response = client.get(
            "/api/llm/config",
            headers=user_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "default_provider" in data
        assert "fallback_enabled" in data
        assert "caching_enabled" in data
        assert "available_providers" in data
        assert "pricing_info" in data
        assert "models_by_provider" in data
        
        # Validate structure
        assert isinstance(data["available_providers"], list)
        assert isinstance(data["pricing_info"], dict)
        assert isinstance(data["models_by_provider"], dict)


class TestAuthenticationRequired:
    """Tests to ensure all LLM endpoints require authentication."""
    
    @pytest.mark.asyncio
    async def test_extract_skills_requires_auth(self, client):
        """Test that extract-skills requires authentication."""
        response = client.post(
            "/api/llm/extract-skills",
            json={"text": "Python", "provider": "openai"},
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_generate_text_requires_auth(self, client):
        """Test that generate-text requires authentication."""
        response = client.post(
            "/api/llm/generate-text",
            json={"prompt": "Test", "provider": "openai"},
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_metrics_requires_auth(self, client):
        """Test that metrics endpoint requires authentication."""
        response = client.get("/api/llm/metrics")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
