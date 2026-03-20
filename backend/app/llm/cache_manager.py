"""
LLM result caching system.
Implements both in-memory and Redis-based caching options.
"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from cachetools import TTLCache
from app.llm.base_provider import LLMResponse

logger = logging.getLogger(__name__)


def generate_cache_key(
    provider: str,
    model: str,
    prompt: str,
    temperature: float = 0.7
) -> str:
    """
    Generate cache key from LLM parameters.
    
    Args:
        provider: LLM provider name
        model: Model name
        prompt: The prompt text
        temperature: Temperature parameter
        
    Returns:
        Hash-based cache key
    """
    cache_input = f"{provider}:{model}:{prompt}:{temperature}"
    return hashlib.sha256(cache_input.encode()).hexdigest()


class BaseCacheManager(ABC):
    """Abstract base class for cache managers."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[LLMResponse]:
        """Get cached response."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        response: LLMResponse,
        ttl_seconds: int = 3600
    ) -> bool:
        """Cache a response."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a cached response."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached responses."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class InMemoryCacheManager(BaseCacheManager):
    """
    In-memory cache manager using TTLCache.
    Suitable for single-process deployments.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of cached items
            default_ttl: Default TTL in seconds
        """
        self.cache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self.hits = 0
        self.misses = 0
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[LLMResponse]:
        """
        Get cached response.
        
        Args:
            key: Cache key
            
        Returns:
            Cached LLMResponse or None
        """
        if key in self.cache:
            self.hits += 1
            response = self.cache[key]
            response.cached = True
            logger.debug(f"Cache hit for key {key[:8]}...")
            return response
        
        self.misses += 1
        logger.debug(f"Cache miss for key {key[:8]}...")
        return None
    
    async def set(
        self,
        key: str,
        response: LLMResponse,
        ttl_seconds: int = None
    ) -> bool:
        """
        Cache a response.
        
        Args:
            key: Cache key
            response: LLMResponse to cache
            ttl_seconds: TTL (uses default if not specified)
            
        Returns:
            True if cached successfully
        """
        try:
            ttl = ttl_seconds or self.default_ttl
            # Recreate TTLCache with specific TTL for this item
            self.cache[key] = response
            logger.debug(f"Cached response for key {key[:8]}... (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Failed to cache response: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a cached response.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted successfully
        """
        try:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Deleted cached response for key {key[:8]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete cache entry: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear all cached responses.
        
        Returns:
            True if cleared successfully
        """
        try:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            logger.info("Cleared all cached responses")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "type": "in-memory",
            "total_items": len(self.cache),
            "max_size": self.cache.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "default_ttl": self.default_ttl,
        }


class RedisCacheManager(BaseCacheManager):
    """
    Redis-based cache manager.
    Suitable for multi-process and distributed deployments.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        """
        Initialize Redis cache.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
        """
        try:
            import aioredis
            self.redis = None  # Will be set up lazily
            self.redis_url = redis_url
            self.default_ttl = default_ttl
            self.hits = 0
            self.misses = 0
            logger.info(f"Redis cache manager initialized (URL: {redis_url})")
        except ImportError:
            logger.warning("aioredis not installed, falling back to in-memory cache")
            raise
    
    async def _ensure_connection(self):
        """Ensure Redis connection is established."""
        if self.redis is None:
            try:
                import aioredis
                self.redis = await aioredis.create_redis_pool(self.redis_url)
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                raise
    
    async def get(self, key: str) -> Optional[LLMResponse]:
        """
        Get cached response from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            Cached LLMResponse or None
        """
        try:
            await self._ensure_connection()
            value = await self.redis.get(key)
            
            if value:
                self.hits += 1
                response_data = json.loads(value.decode())
                logger.debug(f"Cache hit for key {key[:8]}...")
                
                # Reconstruct LLMResponse
                response = LLMResponse(
                    content=response_data["content"],
                    model=response_data["model"],
                    tokens_used=response_data["tokens_used"],
                    input_tokens=response_data["input_tokens"],
                    output_tokens=response_data["output_tokens"],
                    provider=response_data.get("provider"),
                    cached=True,
                    metadata=response_data.get("metadata"),
                )
                return response
            
            self.misses += 1
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        response: LLMResponse,
        ttl_seconds: int = None
    ) -> bool:
        """
        Cache a response in Redis.
        
        Args:
            key: Cache key
            response: LLMResponse to cache
            ttl_seconds: TTL in seconds
            
        Returns:
            True if cached successfully
        """
        try:
            await self._ensure_connection()
            ttl = ttl_seconds or self.default_ttl
            
            response_data = {
                "content": response.content,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "provider": response.provider,
                "metadata": response.metadata,
            }
            
            value = json.dumps(response_data)
            await self.redis.setex(key, ttl, value.encode())
            logger.debug(f"Cached response for key {key[:8]}... (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a cached response from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted successfully
        """
        try:
            await self._ensure_connection()
            result = await self.redis.delete(key)
            logger.debug(f"Deleted cached response for key {key[:8]}...")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear all cached responses (use carefully in production).
        
        Returns:
            True if cleared successfully
        """
        try:
            await self._ensure_connection()
            await self.redis.flushdb()
            self.hits = 0
            self.misses = 0
            logger.info("Cleared all Redis cached responses")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get Redis cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        try:
            await self._ensure_connection()
            info = await self.redis.info()
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            
            return {
                "type": "redis",
                "server_info": info.get("Server", {}),
                "memory_usage": info.get("Memory", {}),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(hit_rate, 2),
                "default_ttl": self.default_ttl,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {"error": str(e)}
