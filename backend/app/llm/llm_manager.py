"""
LLM Manager - Orchestrates LLM operations with caching, fallback, and cost tracking.
Provides a unified interface to all LLM providers.
"""

import logging
import os
from typing import Optional, Dict, Any, List
from app.llm.base_provider import BaseLLMProvider, LLMProvider, LLMModel, LLMResponse
from app.llm.openai_provider import OpenAIProvider
from app.llm.claude_provider import ClaudeProvider
from app.llm.cache_manager import (
    BaseCacheManager,
    InMemoryCacheManager,
    generate_cache_key,
)
from app.llm.cost_tracker import CostTracker
from app.llm.fallback_extractor import FallbackExtractor

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Central LLM manager that orchestrates:
    - Multiple LLM providers
    - Result caching
    - Cost tracking
    - Fallback strategies
    - Error handling
    """
    
    def __init__(
        self,
        cache_manager: Optional[BaseCacheManager] = None,
        cost_tracker: Optional[CostTracker] = None,
        enable_fallback: bool = True,
        default_provider: LLMProvider = LLMProvider.OPENAI,
    ):
        """
        Initialize LLM Manager.
        
        Args:
            cache_manager: Cache manager instance (defaults to in-memory)
            cost_tracker: Cost tracker instance
            enable_fallback: Whether to use fallback extraction
            default_provider: Default LLM provider
        """
        self.cache_manager = cache_manager or InMemoryCacheManager()
        self.cost_tracker = cost_tracker or CostTracker()
        self.enable_fallback = enable_fallback
        self.default_provider = default_provider
        
        # Initialize providers
        self.providers: Dict[LLMProvider, Optional[BaseLLMProvider]] = {
            LLMProvider.OPENAI: self._init_provider(LLMProvider.OPENAI),
            LLMProvider.CLAUDE: self._init_provider(LLMProvider.CLAUDE),
        }
        
        # Metrics
        self.total_cached_calls = 0
        self.total_fallback_calls = 0
        
        logger.info(
            f"LLM Manager initialized",
            extra={
                "default_provider": default_provider.value,
                "fallback_enabled": enable_fallback,
            }
        )
    
    def _init_provider(self, provider: LLMProvider) -> Optional[BaseLLMProvider]:
        """
        Initialize a specific LLM provider.
        
        Args:
            provider: Provider to initialize
            
        Returns:
            Initialized provider or None if not available
        """
        try:
            if provider == LLMProvider.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
                org = os.getenv("OPENAI_ORG_ID")
                if api_key:
                    return OpenAIProvider(api_key, org)
                else:
                    logger.warning("OpenAI API key not found in environment")
                    return None
            
            elif provider == LLMProvider.CLAUDE:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    return ClaudeProvider(api_key)
                else:
                    logger.warning("Anthropic API key not found in environment")
                    return None
            
            return None
        except Exception as e:
            logger.error(f"Failed to initialize {provider.value} provider: {str(e)}")
            return None
    
    async def extract_skills(
        self,
        text: str,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        use_cache: bool = True,
        use_fallback: bool = True,
        user_id: Optional[str] = None,
    ) -> LLMResponse:
        """
        Extract skills from text with caching and fallback support.
        
        Args:
            text: Text to extract skills from
            provider: LLM provider to use (defaults to default_provider)
            model: Model to use
            use_cache: Whether to use cache
            use_fallback: Whether to use fallback on error
            user_id: User ID for cost tracking
            
        Returns:
            LLMResponse with extracted skills
        """
        provider = provider or self.default_provider
        
        # Generate cache key
        cache_key = generate_cache_key(
            provider=provider.value,
            model=model or "default",
            prompt=text,
            temperature=0.3,
        )
        
        # Check cache
        if use_cache:
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                self.total_cached_calls += 1
                logger.info(
                    "Skills extracted from cache",
                    extra={"user_id": user_id, "provider": provider.value}
                )
                return cached_response
        
        # Try LLM provider
        try:
            llm_provider = self.providers.get(provider)
            if not llm_provider:
                logger.warning(f"Provider {provider.value} not available, using fallback")
                return await self._fallback_extract_skills(text, user_id)
            
            response = await llm_provider.extract_skills(text, model)
            
            # Cache result
            if use_cache:
                await self.cache_manager.set(cache_key, response)
            
            # Track cost
            if response.cost:
                await self.cost_tracker.record_cost(
                    provider=response.provider or provider.value,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost=response.cost.total_cost,
                    user_id=user_id,
                    operation="extract_skills",
                )
            
            logger.info(
                "Skills extracted via LLM",
                extra={
                    "user_id": user_id,
                    "provider": provider.value,
                    "cost": response.cost.total_cost if response.cost else None,
                }
            )
            
            return response
        
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            
            if use_fallback and self.enable_fallback:
                logger.info("Falling back to rule-based extraction")
                return await self._fallback_extract_skills(text, user_id)
            else:
                raise
    
    async def _fallback_extract_skills(
        self,
        text: str,
        user_id: Optional[str] = None,
    ) -> LLMResponse:
        """
        Extract skills using rule-based fallback.
        
        Args:
            text: Text to extract skills from
            user_id: User ID for tracking
            
        Returns:
            LLMResponse with fallback extraction
        """
        self.total_fallback_calls += 1
        
        skills = FallbackExtractor.extract_skills(text)
        
        response = LLMResponse(
            content=str({"skills": skills}),
            model="fallback-rule-based",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost=None,
            provider="fallback",
            cached=False,
            metadata={
                "method": "rule-based",
                "skills": skills,
                "extraction_type": "fallback",
            }
        )
        
        logger.info(
            "Skills extracted via fallback",
            extra={
                "user_id": user_id,
                "skills_count": len(skills),
            }
        )
        
        return response
    
    async def generate_text(
        self,
        prompt: str,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        use_cache: bool = True,
        user_id: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using LLM.
        
        Args:
            prompt: The prompt to send
            provider: LLM provider
            model: Model to use
            use_cache: Whether to use cache
            user_id: User ID for tracking
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated text
        """
        provider = provider or self.default_provider
        
        # Generate cache key
        temperature = kwargs.get("temperature", 0.7)
        cache_key = generate_cache_key(
            provider=provider.value,
            model=model or "default",
            prompt=prompt,
            temperature=temperature,
        )
        
        # Check cache
        if use_cache:
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                self.total_cached_calls += 1
                logger.info("Text generated from cache", extra={"user_id": user_id})
                return cached_response
        
        # Try LLM provider
        try:
            llm_provider = self.providers.get(provider)
            if not llm_provider:
                raise ValueError(f"Provider {provider.value} not available")
            
            response = await llm_provider.generate_text(prompt, model, **kwargs)
            
            # Cache result
            if use_cache:
                await self.cache_manager.set(cache_key, response)
            
            # Track cost
            if response.cost:
                await self.cost_tracker.record_cost(
                    provider=response.provider or provider.value,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost=response.cost.total_cost,
                    user_id=user_id,
                    operation="generate_text",
                )
            
            logger.info(
                "Text generated via LLM",
                extra={
                    "user_id": user_id,
                    "provider": provider.value,
                    "cost": response.cost.total_cost if response.cost else None,
                }
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise
    
    async def validate_providers(self) -> Dict[str, bool]:
        """
        Validate all configured providers.
        
        Returns:
            Dictionary mapping provider name to validation result
        """
        results = {}
        
        for provider, instance in self.providers.items():
            if instance:
                try:
                    is_valid = await instance.validate_connection()
                    results[provider.value] = is_valid
                    logger.info(
                        f"Provider validation: {provider.value} = {is_valid}"
                    )
                except Exception as e:
                    logger.error(f"Provider validation failed for {provider.value}: {str(e)}")
                    results[provider.value] = False
            else:
                results[provider.value] = False
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive LLM Manager metrics.
        
        Returns:
            Dictionary with all metrics
        """
        return {
            "total_cached_calls": self.total_cached_calls,
            "total_fallback_calls": self.total_fallback_calls,
            "cache_stats": self.cache_manager.get_stats() if hasattr(
                self.cache_manager, 'get_stats'
            ) else {},
            "cost_stats": self.cost_tracker.get_stats(),
            "default_provider": self.default_provider.value,
            "available_providers": [
                p.value for p, instance in self.providers.items()
                if instance is not None
            ],
        }
    
    def clear_cache(self):
        """Clear all cached responses."""
        self.cache_manager.clear()
        logger.info("LLM cache cleared")
    
    async def get_provider_metrics(
        self,
        provider: LLMProvider
    ) -> Dict[str, Any]:
        """
        Get metrics for a specific provider.
        
        Args:
            provider: Provider to get metrics for
            
        Returns:
            Dictionary with provider metrics
        """
        llm_provider = self.providers.get(provider)
        if llm_provider:
            return llm_provider.get_metrics()
        else:
            return {"error": f"Provider {provider.value} not available"}
