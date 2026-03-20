"""
LLM Integration Routes and API endpoints.
Provides endpoints for LLM operations, caching, cost tracking, and provider management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional

# Import schemas
from app.schemas.llm_schemas import (
    SkillExtractionRequest,
    SkillExtractionResponse,
    SkillExtractionWithConfidence,
    GenerateTextRequest,
    LLMResponseSchema,
    ProviderValidationResponse,
    LLMManagerMetrics,
    CacheControlRequest,
    CacheControlResponse,
    CostForecast,
    LLMConfigResponse,
    ProviderMetrics,
)

# Import LLM components
from app.llm import LLMManager, LLMProvider, LLMModel, FallbackExtractor

# Import auth from existing setup
from app.core.security import verify_token_and_get_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])

# Global LLM Manager instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create LLM Manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager(
            enable_fallback=True,
            default_provider=LLMProvider.OPENAI,
        )
    return _llm_manager


@router.post(
    "/extract-skills",
    response_model=SkillExtractionResponse,
    summary="Extract skills from text",
    description="Extract technical skills using LLM with caching and fallback support"
)
async def extract_skills(
    request: SkillExtractionRequest,
    current_user: User = Depends(verify_token_and_get_user),
    llm_manager: LLMManager = Depends(get_llm_manager),
):
    """
    Extract skills from provided text.
    
    Supports:
    - Multiple LLM providers (OpenAI, Claude)
    - Result caching
    - Automatic fallback to rule-based extraction
    - Cost tracking per user
    """
    try:
        provider = LLMProvider(request.provider.value)
        
        response = await llm_manager.extract_skills(
            text=request.text,
            provider=provider,
            model=request.model.value if request.model else None,
            use_cache=request.use_cache,
            use_fallback=request.use_fallback,
            user_id=str(current_user.id),
        )
        
        # Extract skills from metadata
        skills = response.metadata.get("skills", []) if response.metadata else []
        
        return SkillExtractionResponse(
            skills=skills,
            skill_count=len(skills),
            extraction_method="cached" if response.cached else (
                "fallback" if response.provider == "fallback" else "llm"
            ),
            model=response.model,
            cost=response.cost,
            metadata=response.metadata,
        )
    
    except Exception as e:
        logger.error(f"Skill extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/extract-skills-with-confidence",
    response_model=SkillExtractionWithConfidence,
    summary="Extract skills with confidence scores"
)
async def extract_skills_with_confidence(
    request: SkillExtractionRequest,
    current_user: User = Depends(verify_token_and_get_user),
):
    """Extract skills with confidence scores based on frequency."""
    try:
        skills_with_confidence = FallbackExtractor.extract_skills_with_confidence(
            request.text
        )
        
        return SkillExtractionWithConfidence(
            skills=skills_with_confidence,
            extraction_method="confidence-based",
        )
    except Exception as e:
        logger.error(f"Confidence extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/extract-skills-by-category",
    summary="Extract skills organized by category"
)
async def extract_skills_by_category(
    request: SkillExtractionRequest,
    current_user: User = Depends(verify_token_and_get_user),
):
    """Extract and categorize skills."""
    try:
        categorized = FallbackExtractor.extract_skills_by_category(request.text)
        return categorized
    except Exception as e:
        logger.error(f"Categorized extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/generate-text",
    response_model=LLMResponseSchema,
    summary="Generate text using LLM"
)
async def generate_text(
    request: GenerateTextRequest,
    current_user: User = Depends(verify_token_and_get_user),
    llm_manager: LLMManager = Depends(get_llm_manager),
):
    """
    Generate text using selected LLM provider.
    
    Supports caching and multiple models.
    """
    try:
        provider = LLMProvider(request.provider.value)
        
        response = await llm_manager.generate_text(
            prompt=request.prompt,
            provider=provider,
            model=request.model.value if request.model else None,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            use_cache=request.use_cache,
            user_id=str(current_user.id),
        )
        
        return LLMResponseSchema(
            content=response.content,
            model=response.model,
            tokens_used=response.tokens_used,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            provider=response.provider,
            cached=response.cached,
            metadata=response.metadata,
        )
    except Exception as e:
        logger.error(f"Text generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/providers/validate",
    response_model=ProviderValidationResponse,
    summary="Validate configured LLM providers"
)
async def validate_providers(
    llm_manager: LLMManager = Depends(get_llm_manager),
    current_user: User = Depends(verify_token_and_get_user),
):
    """Validate that all configured LLM providers are operational."""
    try:
        results = await llm_manager.validate_providers()
        
        return ProviderValidationResponse(
            providers=results,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Provider validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics",
    response_model=LLMManagerMetrics,
    summary="Get LLM Manager metrics"
)
async def get_metrics(
    llm_manager: LLMManager = Depends(get_llm_manager),
    current_user: User = Depends(verify_token_and_get_user),
):
    """Get comprehensive LLM Manager metrics and statistics."""
    try:
        metrics = llm_manager.get_metrics()
        
        return LLMManagerMetrics(
            total_cached_calls=metrics["total_cached_calls"],
            total_fallback_calls=metrics["total_fallback_calls"],
            default_provider=metrics["default_provider"],
            available_providers=metrics["available_providers"],
            cache_stats=metrics.get("cache_stats"),
            cost_stats=metrics.get("cost_stats"),
        )
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/costs/stats",
    summary="Get cost tracking statistics"
)
async def get_cost_stats(
    llm_manager: LLMManager = Depends(get_llm_manager),
    current_user: User = Depends(verify_token_and_get_user),
    days: int = Query(default=30, ge=1, le=365),
):
    """Get cost statistics for the specified period."""
    try:
        start_time = datetime.utcnow() - timedelta(days=days)
        
        stats = llm_manager.cost_tracker.get_stats(
            start_time=start_time
        )
        
        return {
            "period_days": days,
            "start_date": start_time.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            **stats,
        }
    except Exception as e:
        logger.error(f"Failed to get cost stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/costs/forecast",
    response_model=CostForecast,
    summary="Forecast future LLM costs"
)
async def forecast_costs(
    llm_manager: LLMManager = Depends(get_llm_manager),
    current_user: User = Depends(verify_token_and_get_user),
    daily_requests: int = Query(default=100, ge=1),
    days: int = Query(default=30, ge=1, le=365),
):
    """Forecast LLM costs based on expected usage."""
    try:
        forecast = llm_manager.cost_tracker.get_usage_forecast(
            daily_requests=daily_requests,
            days=days,
        )
        
        return CostForecast(**forecast)
    except Exception as e:
        logger.error(f"Failed to forecast costs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/cache/control",
    response_model=CacheControlResponse,
    summary="Control cache operations"
)
async def cache_control(
    request: CacheControlRequest,
    current_user: User = Depends(verify_token_and_get_user),
    llm_manager: LLMManager = Depends(get_llm_manager),
):
    """Clear cache or get cache statistics."""
    try:
        if request.action == "clear":
            llm_manager.clear_cache()
            return CacheControlResponse(
                success=True,
                message="Cache cleared successfully"
            )
        
        elif request.action == "get_stats":
            stats = await llm_manager.cache_manager.get_stats()
            return CacheControlResponse(
                success=True,
                message="Cache statistics retrieved",
                stats=stats,
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action: {request.action}"
            )
    
    except Exception as e:
        logger.error(f"Cache control failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/config",
    response_model=LLMConfigResponse,
    summary="Get LLM configuration"
)
async def get_config(
    current_user: User = Depends(verify_token_and_get_user),
):
    """Get current LLM configuration and pricing information."""
    try:
        # Pricing information
        pricing_info = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},
                "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            },
            "claude": {
                "opus": {"input": 15.0, "output": 75.0},
                "sonnet": {"input": 3.0, "output": 15.0},
                "haiku": {"input": 0.25, "output": 1.25},
            },
        }
        
        models_by_provider = {
            "openai": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
            "claude": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        }
        
        return LLMConfigResponse(
            default_provider="openai",
            fallback_enabled=True,
            caching_enabled=True,
            available_providers=["openai", "claude"],
            pricing_info=pricing_info,
            models_by_provider=models_by_provider,
        )
    except Exception as e:
        logger.error(f"Failed to get config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
