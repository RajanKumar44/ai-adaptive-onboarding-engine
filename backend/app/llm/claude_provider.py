"""
Claude (Anthropic) LLM provider implementation.
Supports Claude 3 models (Opus, Sonnet, Haiku).
"""

import json
import logging
from typing import Optional, Dict, Any
from anthropic import AsyncAnthropic, APIError, RateLimitError
from app.llm.base_provider import BaseLLMProvider, LLMResponse, LLMCost, LLMModel

logger = logging.getLogger(__name__)


# Anthropic pricing (per 1M tokens)
CLAUDE_PRICING = {
    "claude-3-opus-20240229": {
        "input": 15.0,
        "output": 75.0,
    },
    "claude-3-sonnet-20240229": {
        "input": 3.0,
        "output": 15.0,
    },
    "claude-3-haiku-20240307": {
        "input": 0.25,
        "output": 1.25,
    },
}

SKILL_EXTRACTION_PROMPT = """Extract all technical skills from the following text. 
Return a JSON object with a 'skills' array containing skill names.
Only include legitimate technical skills (programming languages, frameworks, tools, etc.).

Text:
{text}

Return only valid JSON, no additional text."""


class ClaudeProvider(BaseLLMProvider):
    """
    Claude (Anthropic) LLM provider implementation.
    Uses the Anthropic API for text generation and skill extraction.
    """
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        """
        Initialize Claude provider.
        
        Args:
            api_key: Anthropic API key
            organization: Optional organization (not used by Anthropic)
        """
        super().__init__(api_key, organization)
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = LLMModel.CLAUDE_3_HAIKU.value
    
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
        Generate text using Claude API.
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to claude-3-haiku)
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
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            
            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
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
                provider="claude",
                cached=False,
                metadata={"stop_reason": response.stop_reason},
            )
            
            self.update_metrics(llm_response)
            logger.info(
                f"Claude API call successful",
                extra={
                    "model": model,
                    "tokens": total_tokens,
                    "cost": cost_value,
                }
            )
            
            return llm_response
            
        except RateLimitError as e:
            logger.error(f"Claude rate limit exceeded: {str(e)}")
            raise
        except APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise
    
    async def extract_skills(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Extract skills from text using Claude.
        
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
        Calculate cost for Claude API call.
        
        Args:
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        if model not in CLAUDE_PRICING:
            logger.warning(f"Unknown model for cost calculation: {model}")
            return 0.0
        
        pricing = CLAUDE_PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    async def validate_connection(self) -> bool:
        """
        Validate Claude API connection.
        
        Returns:
            True if connection is valid
        """
        try:
            # Use a minimal API call to validate connection
            response = await self.client.messages.create(
                model=self.default_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            logger.error(f"Claude connection validation failed: {str(e)}")
            return False
