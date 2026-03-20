"""
Pydantic schemas for LLM integration endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class LLMProviderEnum(str, Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    CLAUDE = "claude"


class LLMModelEnum(str, Enum):
    """Available LLM models."""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


class SkillExtractionRequest(BaseModel):
    """Request for skill extraction."""
    text: str = Field(..., description="Text to extract skills from", min_length=1)
    provider: Optional[LLMProviderEnum] = Field(
        default=LLMProviderEnum.OPENAI,
        description="LLM provider to use"
    )
    model: Optional[LLMModelEnum] = None
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached results"
    )
    use_fallback: bool = Field(
        default=True,
        description="Whether to use fallback extraction if LLM fails"
    )


class GenerateTextRequest(BaseModel):
    """Request for text generation."""
    prompt: str = Field(..., description="The prompt", min_length=1)
    provider: Optional[LLMProviderEnum] = Field(
        default=LLMProviderEnum.OPENAI,
        description="LLM provider"
    )
    model: Optional[LLMModelEnum] = None
    max_tokens: int = Field(default=2000, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    use_cache: bool = Field(default=True)


class LLMCostData(BaseModel):
    """LLM API call cost data."""
    model: str
    input_tokens: int
    output_tokens: int
    total_cost: float
    currency: str = "USD"
    timestamp: datetime


class LLMResponseSchema(BaseModel):
    """Response schema for LLM operations."""
    content: str = Field(..., description="Generated or extracted content")
    model: str = Field(..., description="Model used")
    tokens_used: int = Field(..., description="Total tokens used")
    input_tokens: int
    output_tokens: int
    cost: Optional[LLMCostData] = None
    provider: Optional[str] = None
    cached: bool = Field(default=False, description="Whether result was cached")
    metadata: Optional[Dict[str, Any]] = None


class SkillExtractionResponse(BaseModel):
    """Response for skill extraction."""
    skills: List[str] = Field(..., description="Extracted skills")
    skill_count: int = Field(..., description="Number of skills found")
    extraction_method: str = Field(
        ...,
        description="Method used (llm, fallback, cached)"
    )
    model: str
    cost: Optional[LLMCostData] = None
    metadata: Optional[Dict[str, Any]] = None


class SkillExtractionWithConfidence(BaseModel):
    """Skill extraction with confidence scores."""
    skills: Dict[str, float] = Field(
        ...,
        description="Skills with confidence scores (0-1)"
    )
    extraction_method: str


class ProviderMetrics(BaseModel):
    """Metrics for an LLM provider."""
    total_requests: int
    total_tokens: int
    total_cost: float
    avg_tokens_per_request: float
    avg_cost_per_request: float


class CachStats(BaseModel):
    """Cache statistics."""
    type: str
    total_items: int
    max_size: int
    hits: int
    misses: int
    hit_rate: float
    default_ttl: int


class CostStats(BaseModel):
    """Cost tracking statistics."""
    total_requests: int
    total_cost: float
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    avg_cost_per_request: float
    avg_tokens_per_request: float
    cost_by_provider: Dict[str, float]
    cost_by_model: Dict[str, float]
    cost_by_user: Optional[Dict[str, float]] = None


class LLMManagerMetrics(BaseModel):
    """Overall LLM Manager metrics."""
    total_cached_calls: int
    total_fallback_calls: int
    default_provider: str
    available_providers: List[str]
    cache_stats: Optional[Dict[str, Any]] = None
    cost_stats: Optional[Dict[str, Any]] = None


class ProviderValidationResponse(BaseModel):
    """Response for provider validation."""
    providers: Dict[str, bool] = Field(
        ...,
        description="Mapping of provider names to validation results"
    )
    timestamp: datetime


class CostForecast(BaseModel):
    """Cost forecast data."""
    daily_requests: int
    forecast_days: int
    total_projected_requests: int
    avg_cost_per_request: float
    projected_total_cost: float
    projected_monthly_cost: float


class CacheControlRequest(BaseModel):
    """Request to control cache."""
    action: str = Field(..., description="Action: clear, get_stats")
    key: Optional[str] = None


class CacheControlResponse(BaseModel):
    """Response from cache control."""
    success: bool
    message: str
    stats: Optional[Dict[str, Any]] = None


class LLMConfigResponse(BaseModel):
    """LLM configuration details."""
    default_provider: str
    fallback_enabled: bool
    caching_enabled: bool
    available_providers: List[str]
    pricing_info: Dict[str, Dict[str, float]]
    models_by_provider: Dict[str, List[str]]
