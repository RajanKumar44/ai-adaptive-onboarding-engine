"""
Google Gemini LLM provider implementation.
Supports Gemini 1.5 Pro, Gemini 1.5 Flash, and Gemini Pro models.
"""

import json
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from app.llm.base_provider import BaseLLMProvider, LLMResponse, LLMCost, LLMModel

logger = logging.getLogger(__name__)


# Google Gemini pricing (per 1M tokens)
GEMINI_PRICING = {
    "gemini-1.5-pro": {
        "input": 1.25,      # $1.25 per 1M input tokens (0.00000125 per token)
        "output": 5.00,     # $5.00 per 1M output tokens (0.000005 per token)
    },
    "gemini-1.5-flash": {
        "input": 0.075,     # $0.075 per 1M input tokens (0.000000075 per token)
        "output": 0.30,     # $0.30 per 1M output tokens (0.0000003 per token)
    },
    "gemini-pro": {
        "input": 0.5,       # $0.5 per 1M input tokens (0.0000005 per token)
        "output": 1.5,      # $1.5 per 1M output tokens (0.0000015 per token)
    },
}

SKILL_EXTRACTION_PROMPT = """Extract all technical skills from the following text. 
Return a JSON object with a 'skills' array containing skill names.
Only include legitimate technical skills (programming languages, frameworks, tools, etc.).

Text:
{text}

Return only valid JSON, no additional text."""


class GoogleGeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider implementation.
    Uses the Google Generative AI API for text generation and skill extraction.
    """
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        """
        Initialize Google Gemini provider.
        
        Args:
            api_key: Google Gemini API key
            organization: Optional organization ID (not used for Gemini)
        """
        super().__init__(api_key, organization)
        genai.configure(api_key=api_key)
        self.default_model = LLMModel.GEMINI_1_5_FLASH.value
    
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
        Generate text using Google Gemini API.
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to gemini-1.5-flash)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter
            top_p: Nucleus sampling parameter
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            GoogleAPIError: For API errors
        """
        try:
            model = model or self.default_model
            
            # Create model instance
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            
            safety_settings = [
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
                }
            ]
            
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            
            # Generate content
            response = gemini_model.generate_content(prompt)
            
            content = response.text if response.text else ""
            
            # Gemini doesn't provide token counts directly, estimate from text
            input_tokens = len(prompt.split()) * 1.3  # Approximate
            output_tokens = len(content.split()) * 1.3  # Approximate
            
            cost = self.get_model_cost(model, int(input_tokens), int(output_tokens))
            
            logger.info(
                f"Generated text via Gemini",
                extra={
                    "model": model,
                    "input_tokens": int(input_tokens),
                    "output_tokens": int(output_tokens),
                    "cost": cost.total_cost,
                }
            )
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=int(input_tokens + output_tokens),
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                cost=cost,
                provider="gemini",
                metadata={"response_type": "text"}
            )
            
        except GoogleAPIError as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Gemini text generation: {str(e)}")
            raise
    
    async def extract_skills(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Extract technical skills from text using Gemini.
        
        Args:
            text: Text to extract skills from
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            List of extracted skills
        """
        try:
            prompt = SKILL_EXTRACTION_PROMPT.format(text=text)
            response = await self.generate_text(
                prompt=prompt,
                model=model,
                max_tokens=1000,
                **kwargs
            )
            
            # Parse JSON response
            try:
                result = json.loads(response.content)
                skills = result.get("skills", [])
                
                # Ensure all skills are lowercase and stripped
                skills = [s.strip().lower() for s in skills if s.strip()]
                
                logger.info(
                    f"Extracted {len(skills)} skills via Gemini",
                    extra={"skills": skills}
                )
                
                return skills
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response from Gemini")
                return []
            
        except Exception as e:
            logger.error(f"Error extracting skills via Gemini: {str(e)}")
            raise
    
    def get_model_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> LLMCost:
        """
        Calculate cost for Gemini API call.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            LLMCost object with cost information
        """
        pricing = GEMINI_PRICING.get(model, GEMINI_PRICING["gemini-1.5-flash"])
        
        # Pricing is per 1M tokens, convert to per token
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return LLMCost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=total_cost,
            currency="USD"
        )
    
    async def validate_connection(self) -> bool:
        """
        Validate connection to Gemini API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # List available models to test connection
            models = genai.list_models()
            
            # Check if any Gemini models are available
            for model in models:
                if "gemini" in model.name.lower():
                    logger.info("Gemini API connection validated")
                    return True
            
            logger.warning("No Gemini models found in API response")
            return False
            
        except Exception as e:
            logger.error(f"Failed to validate Gemini connection: {str(e)}")
            return False
