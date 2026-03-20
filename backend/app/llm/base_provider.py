"""
Base LLM provider abstraction.
Defines interface for all LLM provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROK = "grok"  # Future support


class LLMModel(str, Enum):
    """Supported LLM models."""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_PRO = "gemini-pro"


@dataclass
class LLMCost:
    """Track cost of LLM API call."""
    model: str
    input_tokens: int
    output_tokens: int
    total_cost: float
    currency: str = "USD"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    model: str
    tokens_used: int
    input_tokens: int
    output_tokens: int
    cost: Optional[LLMCost] = None
    provider: Optional[str] = None
    cached: bool = False
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    All LLM providers must implement this interface.
    """
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
            organization: Optional organization ID
        """
        self.api_key = api_key
        self.organization = organization
        self.total_cost = 0.0
        self.total_requests = 0
        self.total_tokens = 0
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model to use
            max_tokens: Maximum tokens in response
            temperature: Creativity/randomness parameter
            top_p: Nucleus sampling parameter
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with generated content and metadata
        """
        pass
    
    @abstractmethod
    async def extract_skills(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Extract skills from text using LLM.
        
        Args:
            text: Text to extract skills from
            model: Model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with extracted skills
        """
        pass
    
    @abstractmethod
    def get_model_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for API call.
        
        Args:
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate API connection is working.
        
        Returns:
            True if connection is valid
        """
        pass
    
    def update_metrics(self, response: LLMResponse):
        """
        Update provider metrics after successful API call.
        
        Args:
            response: LLMResponse with cost information
        """
        self.total_requests += 1
        self.total_tokens += response.tokens_used
        if response.cost:
            self.total_cost += response.cost.total_cost
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get provider usage metrics.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "avg_tokens_per_request": (
                round(self.total_tokens / self.total_requests, 2)
                if self.total_requests > 0
                else 0
            ),
            "avg_cost_per_request": (
                round(self.total_cost / self.total_requests, 4)
                if self.total_requests > 0
                else 0
            ),
        }
