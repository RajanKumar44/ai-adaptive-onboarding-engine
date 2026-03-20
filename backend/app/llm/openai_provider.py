"""
OpenAI LLM provider implementation.
Supports GPT-4, GPT-4 Turbo, and GPT-3.5-turbo models.
"""

import json
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI, RateLimitError, APIError
from app.llm.base_provider import BaseLLMProvider, LLMResponse, LLMCost, LLMModel

logger = logging.getLogger(__name__)


# OpenAI pricing (per 1K tokens)
OPENAI_PRICING = {
    "gpt-4": {
        "input": 0.03,
        "output": 0.06,
    },
    "gpt-4-turbo-preview": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-3.5-turbo": {
        "input": 0.0005,
        "output": 0.0015,
    },
}

SKILL_EXTRACTION_PROMPT = """Extract all technical skills from the following text. 
Return a JSON object with a 'skills' array containing skill names.
Only include legitimate technical skills (programming languages, frameworks, tools, etc.).

Text:
{text}

Return only valid JSON, no additional text."""


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider implementation.
    Uses the OpenAI API for text generation and skill extraction.
    """
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            organization: Optional organization ID
        """
        super().__init__(api_key, organization)
        self.client = AsyncOpenAI(api_key=api_key, organization=organization)
        self.default_model = LLMModel.GPT_35_TURBO.value
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to gpt-3.5-turbo)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter
            top_p: Nucleus sampling parameter
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            RateLimitError: If API rate limit exceeded
            APIError: For other API errors
        """
        try:
            model = model or self.default_model
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            cost_value = self.get_model_cost(model, input_tokens, output_tokens)
            cost = LLMCost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_cost=cost_value,
            )
            
            llm_response = LLMResponse(
                content=content,
                model=model,
                tokens_used=total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                provider="openai",
                cached=False,
                metadata={"finish_reason": response.choices[0].finish_reason},
            )
            
            self.update_metrics(llm_response)
            logger.info(
                f"OpenAI API call successful",
                extra={
                    "model": model,
                    "tokens": total_tokens,
                    "cost": cost_value,
                }
            )
            
            return llm_response
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def extract_skills(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Extract skills from text using OpenAI.
        
        Args:
            text: Text to extract skills from
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with extracted skills as JSON
        """
        prompt = SKILL_EXTRACTION_PROMPT.format(text=text)
        
        response = await self.generate_text(
            prompt=prompt,
            model=model,
            max_tokens=500,
            temperature=0.3,  # Lower temperature for consistent results
            **kwargs
        )
        
        # Parse JSON from response
        try:
            parsed = json.loads(response.content)
            response.metadata = response.metadata or {}
            response.metadata["skills"] = parsed.get("skills", [])
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse skill extraction JSON: {str(e)}")
            response.metadata = response.metadata or {}
            response.metadata["skills"] = []
            response.metadata["parse_error"] = str(e)
        
        return response
    
    def get_model_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for OpenAI API call.
        
        Args:
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        if model not in OPENAI_PRICING:
            logger.warning(f"Unknown model for cost calculation: {model}")
            return 0.0
        
        pricing = OPENAI_PRICING[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    async def validate_connection(self) -> bool:
        """
        Validate OpenAI API connection.
        
        Returns:
            True if connection is valid
        """
        try:
            response = await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {str(e)}")
            return False
