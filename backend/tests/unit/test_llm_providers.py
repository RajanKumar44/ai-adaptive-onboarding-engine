"""
Unit tests for LLM providers and components.
Tests cache managers, cost tracking, fallback extractor, and provider implementations.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import LLM components
from app.llm import (
    LLMProvider, LLMModel, LLMResponse, LLMCost,
    InMemoryCacheManager, generate_cache_key,
    CostTracker, CostRecord, FallbackExtractor,
    OpenAIProvider, ClaudeProvider, LLMManager,
)


# ============================================================================
# TESTS FOR CACHE MANAGER
# ============================================================================

class TestInMemoryCacheManager:
    """Tests for in-memory cache manager."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance."""
        return InMemoryCacheManager(max_size=100, default_ttl=3600)
    
    @pytest.mark.asyncio
    async def test_cache_get_miss(self, cache_manager):
        """Test cache miss returns None."""
        result = await cache_manager.get("nonexistent_key")
        assert result is None
        assert cache_manager.misses >= 1
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache_manager):
        """Test setting and retrieving cached value."""
        response = LLMResponse(
            content="test content",
            model="test-model",
            tokens_used=100,
            input_tokens=50,
            output_tokens=50,
        )
        
        key = "test_key"
        await cache_manager.set(key, response)
        
        cached = await cache_manager.get(key)
        assert cached is not None
        assert cached.content == "test content"
        assert cached.cached is True
    
    @pytest.mark.asyncio
    async def test_cache_delete(self, cache_manager):
        """Test deleting cached item."""
        response = LLMResponse(
            content="test", model="test-model", tokens_used=10,
            input_tokens=5, output_tokens=5
        )
        
        key = "test_key"
        await cache_manager.set(key, response)
        
        # Verify it's cached
        cached = await cache_manager.get(key)
        assert cached is not None
        
        # Delete it
        deleted = await cache_manager.delete(key)
        assert deleted is True
        
        # Verify it's gone
        cached = await cache_manager.get(key)
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_cache_clear(self, cache_manager):
        """Test clearing all cache."""
        response = LLMResponse(
            content="test", model="test-model", tokens_used=10,
            input_tokens=5, output_tokens=5
        )
        
        # Add multiple items
        for i in range(5):
            await cache_manager.set(f"key_{i}", response)
        
        # Clear cache
        result = await cache_manager.clear()
        assert result is True
        
        # Verify empty
        cached = await cache_manager.get("key_0")
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate(self, cache_manager):
        """Test cache hit rate calculation."""
        response = LLMResponse(
            content="test", model="test-model", tokens_used=10,
            input_tokens=5, output_tokens=5
        )
        
        await cache_manager.set("key_1", response)
        
        # 2 hits
        await cache_manager.get("key_1")
        await cache_manager.get("key_1")
        
        # 1 miss
        await cache_manager.get("nonexistent")
        
        stats = await cache_manager.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] >= 1
        assert stats["hit_rate"] > 0


class TestCacheKeyGeneration:
    """Tests for cache key generation."""
    
    def test_cache_key_uniqueness(self):
        """Test that different inputs generate different keys."""
        key1 = generate_cache_key("openai", "gpt-4", "prompt1", 0.7)
        key2 = generate_cache_key("openai", "gpt-4", "prompt2", 0.7)
        key3 = generate_cache_key("claude", "claude3", "prompt1", 0.7)
        
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3
    
    def test_cache_key_consistency(self):
        """Test that same inputs always generate same key."""
        params = ("openai", "gpt-4", "same prompt", 0.7)
        
        key1 = generate_cache_key(*params)
        key2 = generate_cache_key(*params)
        
        assert key1 == key2


# ============================================================================
# TESTS FOR COST TRACKER
# ============================================================================

class TestCostTracker:
    """Tests for cost tracking system."""
    
    @pytest.fixture
    def cost_tracker(self):
        """Create cost tracker instance."""
        return CostTracker()
    
    @pytest.mark.asyncio
    async def test_record_cost(self, cost_tracker):
        """Test recording a cost."""
        record = await cost_tracker.record_cost(
            provider="openai",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            user_id="user-123",
            operation="generate_text",
        )
        
        assert record.provider == "openai"
        assert record.model == "gpt-4"
        assert record.total_tokens == 150
        assert record.cost == 0.01
    
    @pytest.mark.asyncio
    async def test_get_costs_with_filtering(self, cost_tracker):
        """Test retrieving costs with filters."""
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01, user_id="user-1"
        )
        await cost_tracker.record_cost(
            provider="claude", model="claude3",
            input_tokens=100, output_tokens=50, cost=0.02, user_id="user-2"
        )
        
        openai_costs = cost_tracker.get_costs(provider="openai")
        assert len(openai_costs) == 1
        assert openai_costs[0].provider == "openai"
        
        user1_costs = cost_tracker.get_costs(user_id="user-1")
        assert len(user1_costs) == 1
    
    @pytest.mark.asyncio
    async def test_get_total_cost(self, cost_tracker):
        """Test calculating total cost."""
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01
        )
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01
        )
        
        total = cost_tracker.get_total_cost()
        assert total == 0.02
    
    @pytest.mark.asyncio
    async def test_cost_by_provider(self, cost_tracker):
        """Test costs grouped by provider."""
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01
        )
        await cost_tracker.record_cost(
            provider="claude", model="claude3",
            input_tokens=100, output_tokens=50, cost=0.02
        )
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01
        )
        
        by_provider = cost_tracker.get_cost_by_provider()
        assert by_provider["openai"] == 0.02
        assert by_provider["claude"] == 0.02
    
    @pytest.mark.asyncio
    async def test_cost_forecast(self, cost_tracker):
        """Test cost forecasting."""
        # Add some historical data
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01
        )
        await cost_tracker.record_cost(
            provider="openai", model="gpt-4",
            input_tokens=100, output_tokens=50, cost=0.01
        )
        
        forecast = cost_tracker.get_usage_forecast(
            daily_requests=100,
            days=30
        )
        
        assert forecast["daily_requests"] == 100
        assert forecast["forecast_days"] == 30
        assert forecast["total_projected_requests"] == 3000
        assert forecast["projected_total_cost"] > 0


# ============================================================================
# TESTS FOR FALLBACK EXTRACTOR
# ============================================================================

class TestFallbackExtractor:
    """Tests for rule-based skill extraction fallback."""
    
    def test_extract_skills_basic(self):
        """Test basic skill extraction."""
        text = "I know Python, JavaScript, and React"
        skills = FallbackExtractor.extract_skills(text)
        
        assert "python" in skills or "Python" in [s.lower() for s in skills]
        assert len(skills) >= 2
    
    def test_extract_skills_case_insensitive(self):
        """Test case-insensitive extraction."""
        text_lower = "I use python and django"
        text_upper = "I use PYTHON and DJANGO"
        
        skills_lower = FallbackExtractor.extract_skills(text_lower)
        skills_upper = FallbackExtractor.extract_skills(text_upper)
        
        assert len(skills_lower) == len(skills_upper)
    
    def test_extract_skills_with_aliases(self):
        """Test skill extraction with aliases."""
        text = "I work with nodejs and github"
        skills = FallbackExtractor.extract_skills(text)
        
        # Should match node.js from nodejs and git from github
        assert len(skills) > 0
    
    def test_extract_skills_with_confidence(self):
        """Test skill extraction with confidence scores."""
        text = "Python Python Python JavaScript JavaScript"
        skills = FallbackExtractor.extract_skills_with_confidence(text)
        
        # Python should have higher confidence than JavaScript
        assert len(skills) > 0
    
    def test_extract_skills_by_category(self):
        """Test skill extraction by category."""
        text = """
        I'm proficient in Python, JavaScript, and TypeScript.
        I work with React, Angular, and Vue.
        Databases: PostgreSQL, MongoDB, Redis.
        Cloud: AWS, Azure, GCP.
        Tools: Docker, Kubernetes, Git, Jenkins.
        """
        
        categories = FallbackExtractor.extract_skills_by_category(text)
        
        assert "programming_languages" in categories
        assert "frameworks" in categories
        assert "databases" in categories or "other" in categories


# ============================================================================
# TESTS FOR LLM MANAGER
# ============================================================================

class TestLLMManager:
    """Tests for LLM Manager orchestrator."""
    
    @pytest.fixture
    def llm_manager(self):
        """Create LLM manager instance."""
        cache = InMemoryCacheManager()
        cost_tracker = CostTracker()
        return LLMManager(
            cache_manager=cache,
            cost_tracker=cost_tracker,
            enable_fallback=True,
        )
    
    @pytest.mark.asyncio
    async def test_fallback_extraction_when_provider_unavailable(self, llm_manager):
        """Test fallback extraction when provider is not available."""
        # Mock providers to be None
        llm_manager.providers[LLMProvider.OPENAI] = None
        
        response = await llm_manager.extract_skills(
            text="I know Python and JavaScript",
            use_fallback=True
        )
        
        assert response.provider == "fallback"
        assert response.metadata is not None
        assert "skills" in response.metadata
        assert len(response.metadata["skills"]) > 0
    
    @pytest.mark.asyncio
    async def test_cache_metrics(self, llm_manager):
        """Test cache metrics tracking."""
        # First call creates cache entry
        text = "Python and JavaScript"
        response1 = await llm_manager._fallback_extract_skills(text)
        
        # Verify metrics
        metrics = llm_manager.get_metrics()
        assert metrics["total_fallback_calls"] >= 1
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, llm_manager):
        """Test cache clearing."""
        llm_manager.clear_cache()
        
        # Cache should be cleared
        stats = await llm_manager.cache_manager.get_stats()
        assert stats["hits"] == 0


# ============================================================================
# TESTS FOR OPENAI PRICING
# ============================================================================

class TestOpenAIProvider:
    """Tests for OpenAI provider pricing and calculations."""
    
    def test_gpt4_pricing(self):
        """Test GPT-4 pricing calculation."""
        provider = OpenAIProvider(api_key="test_key")
        
        cost = provider.get_model_cost("gpt-4", 1000, 500)
        
        # GPT-4: $0.03 per 1K input, $0.06 per 1K output
        # 1000 tokens * 0.03/1000 = 0.03
        # 500 tokens * 0.06/1000 = 0.03
        # Total = 0.06
        assert cost > 0
        assert cost < 0.1
    
    def test_gpt35_pricing(self):
        """Test GPT-3.5 turbo pricing (cheaper)."""
        provider = OpenAIProvider(api_key="test_key")
        
        cost_35 = provider.get_model_cost("gpt-3.5-turbo", 1000, 500)
        cost_4 = provider.get_model_cost("gpt-4", 1000, 500)
        
        # GPT-3.5 should be cheaper than GPT-4
        assert cost_35 < cost_4


class TestClaudeProviding:
    """Tests for Claude provider pricing."""
    
    def test_claude_pricing(self):
        """Test Claude pricing calculations."""
        provider = ClaudeProvider(api_key="test_key")
        
        cost = provider.get_model_cost(
            "claude-3-haiku-20240307",
            1000000,  # 1M tokens
            500000,   # 500K tokens
        )
        
        # Should be > 0
        assert cost > 0


class TestGeminiProvider:
    """Tests for Google Gemini provider."""
    
    def test_gemini_pro_pricing(self):
        """Test Gemini Pro pricing calculations."""
        from app.llm import GoogleGeminiProvider
        
        provider = GoogleGeminiProvider(api_key="test_key")
        
        cost = provider.get_model_cost(
            "gemini-pro",
            1000000,  # 1M tokens
            500000,   # 500K tokens
        )
        
        # Gemini Pro: $0.5 per 1M input, $1.5 per 1M output
        # 1M tokens: $0.5, 500K tokens: $0.75, total: $1.25
        assert cost.total_cost > 0
        assert cost.model == "gemini-pro"
        assert cost.input_tokens == 1000000
        assert cost.output_tokens == 500000
    
    def test_gemini_flash_pricing(self):
        """Test Gemini 1.5 Flash pricing (most affordable)."""
        from app.llm import GoogleGeminiProvider
        
        provider = GoogleGeminiProvider(api_key="test_key")
        
        flash_cost = provider.get_model_cost(
            "gemini-1.5-flash",
            1000000,  # 1M tokens
            1000000,  # 1M tokens
        )
        
        pro_cost = provider.get_model_cost(
            "gemini-pro",
            1000000,  # 1M tokens
            1000000,  # 1M tokens
        )
        
        # Flash should be cheaper than Pro
        assert flash_cost.total_cost < pro_cost.total_cost
    
    def test_gemini_5_pro_pricing(self):
        """Test Gemini 1.5 Pro pricing (most capable)."""
        from app.llm import GoogleGeminiProvider
        
        provider = GoogleGeminiProvider(api_key="test_key")
        
        cost = provider.get_model_cost(
            "gemini-1.5-pro",
            1000000,  # 1M tokens
            1000000,  # 1M tokens
        )
        
        # Gemini 1.5 Pro: $1.25 per 1M input, $5.00 per 1M output
        # Total: $1.25 + $5.00 = $6.25
        expected_cost = 1.25 + 5.00
        assert abs(cost.total_cost - expected_cost) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
