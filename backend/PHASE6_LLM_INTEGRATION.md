"""
Phase 6: LLM Integration - Comprehensive Documentation

This document covers the complete LLM integration implementation,
including architecture, usage, configuration, and examples.
"""

# PHASE 6: LLM INTEGRATION - COMPLETE DOCUMENTATION

## Executive Summary

**Phase 6** implements enterprise-grade LLM integration with:
- ✅ Support for multiple LLM providers (OpenAI, Claude)
- ✅ Intelligent result caching system
- ✅ Comprehensive cost tracking
- ✅ Rule-based fallback extraction
- ✅ Error handling and resilience
- ✅ Full REST API endpoints
- ✅ 50+ unit and integration tests

**Deliverables**: 8 modules (2,600+ LOC), 11 API endpoints, 2 test files (65+ test cases)

---

## Architecture Overview

### Module Structure

```
app/llm/
├── __init__.py                 # Module exports
├── base_provider.py            # Abstract LLM provider interface
├── openai_provider.py          # OpenAI implementation
├── claude_provider.py          # Claude (Anthropic) implementation
├── cache_manager.py            # Caching system (in-memory + Redis)
├── cost_tracker.py             # Cost tracking and analytics
├── fallback_extractor.py       # Rule-based extraction fallback
└── llm_manager.py              # Orchestrator

routes/
├── llm_routes.py               # API endpoints

schemas/
├── llm_schemas.py              # Pydantic models
```

### Component Interactions

```
User Request
    ↓
LLMManager (Orchestrator)
    ├→ Cache Check (InMemoryCacheManager)
    │   └→ Return cached result if hit
    │
    ├→ LLM Provider Selection
    │   ├→ OpenAIProvider (GPT models)
    │   ├→ ClaudeProvider (Claude models)
    │   └→ Or FallbackExtractor (rule-based)
    │
    ├→ Cost Tracking (CostTracker)
    │   └→ Record API call cost
    │
    └→ Response to Client
```

---

## Configuration & Setup

### Environment Variables

```bash
# OpenAI Configuration
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Optional

# Anthropic Configuration
export ANTHROPIC_API_KEY="sk-ant-..."

# Cache Configuration (optional)
export REDIS_URL="redis://localhost:6379"
```

### Dependencies

```
openai==1.3.9                  # OpenAI API client
anthropic==0.7.1              # Anthropic API client
redis==5.0.1                  # Redis caching
cachetools==5.3.2             # TTL cache utilities
aioredis==2.0.1               # Async Redis
```

### Initialization (in main.py)

The LLM routes are automatically initialized when the application starts:

```python
from app.routes.llm_routes import router as llm_router
app.include_router(llm_router)  # Adds /api/llm/* endpoints
```

The LLMManager is lazily initialized on first use:

```python
from app.llm import LLMManager

# Will be created on first LLM request
manager = LLMManager(
    cache_manager=InMemoryCacheManager(),
    cost_tracker=CostTracker(),
    enable_fallback=True,
    default_provider=LLMProvider.OPENAI,
)
```

---

## API Endpoints

All endpoints require authentication (JWT token in Authorization header).

### 1. Skill Extraction

**POST /api/llm/extract-skills**

Extract technical skills from text using LLM.

```bash
curl -X POST http://localhost:8000/api/llm/extract-skills \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I have 5 years experience with Python, Django, PostgreSQL, Docker, and AWS.",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "use_cache": true,
    "use_fallback": true
  }'
```

**Response**:
```json
{
  "skills": ["python", "django", "postgresql", "docker", "aws"],
  "skill_count": 5,
  "extraction_method": "llm",
  "model": "gpt-3.5-turbo",
  "cost": {
    "model": "gpt-3.5-turbo",
    "input_tokens": 45,
    "output_tokens": 28,
    "total_cost": 0.000065,
    "currency": "USD"
  },
  "metadata": {
    "skills": ["python", "django", "postgresql", "docker", "aws"]
  }
}
```

### 2. Skill Extraction with Confidence

**POST /api/llm/extract-skills-with-confidence**

Extract skills with confidence scores (0-1) based on frequency.

```bash
curl -X POST http://localhost:8000/api/llm/extract-skills-with-confidence \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python Python Python JavaScript JavaScript React framework..."
  }'
```

**Response**:
```json
{
  "skills": {
    "python": 0.95,
    "javascript": 0.75,
    "react": 0.6
  },
  "extraction_method": "confidence-based"
}
```

### 3. Categorized Skill Extraction

**POST /api/llm/extract-skills-by-category**

Extract and categorize skills.

```bash
curl -X POST http://localhost:8000/api/llm/extract-skills-by-category \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Expert in Python and JavaScript. React and Django frameworks. PostgreSQL databases."
  }'
```

**Response**:
```json
{
  "programming_languages": ["python", "javascript"],
  "frameworks": ["react", "django"],
  "databases": ["postgresql"]
}
```

### 4. Text Generation

**POST /api/llm/generate-text**

Generate text using selected LLM.

```bash
curl -X POST http://localhost:8000/api/llm/generate-text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain the benefits of Python for data science in 100 words",
    "provider": "openai",
    "model": "gpt-4",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 1.0
  }'
```

### 5. Provider Validation

**GET /api/llm/providers/validate**

Validate all configured LLM providers.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/llm/providers/validate
```

**Response**:
```json
{
  "providers": {
    "openai": true,
    "claude": false
  },
  "timestamp": "2024-03-20T10:30:00Z"
}
```

### 6. LLM Metrics

**GET /api/llm/metrics**

Get comprehensive metrics and statistics.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/llm/metrics
```

**Response**:
```json
{
  "total_cached_calls": 42,
  "total_fallback_calls": 5,
  "default_provider": "openai",
  "available_providers": ["openai", "claude"],
  "cache_stats": {
    "type": "in-memory",
    "total_items": 23,
    "hits": 42,
    "misses": 15,
    "hit_rate": 73.68
  },
  "cost_stats": {
    "total_requests": 57,
    "total_cost": 0.2345,
    "avg_cost_per_request": 0.00411
  }
}
```

### 7. Cost Statistics

**GET /api/llm/costs/stats**

Get cost tracking statistics for a period.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/llm/costs/stats?days=30"
```

### 8. Cost Forecast

**GET /api/llm/costs/forecast**

Forecast future costs based on usage.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/llm/costs/forecast?daily_requests=100&days=30"
```

**Response**:
```json
{
  "daily_requests": 100,
  "forecast_days": 30,
  "total_projected_requests": 3000,
  "avg_cost_per_request": 0.00411,
  "projected_total_cost": 12.33,
  "projected_monthly_cost": 123.30
}
```

### 9. Cache Control

**POST /api/llm/cache/control**

Clear cache or get cache statistics.

```bash
# Clear cache
curl -X POST http://localhost:8000/api/llm/cache/control \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "clear"}'

# Get cache stats
curl -X POST http://localhost:8000/api/llm/cache/control \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "get_stats"}'
```

### 10. LLM Configuration

**GET /api/llm/config**

Get current LLM configuration and pricing information.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/llm/config
```

**Response**:
```json
{
  "default_provider": "openai",
  "fallback_enabled": true,
  "caching_enabled": true,
  "available_providers": ["openai", "claude"],
  "pricing_info": {
    "openai": {
      "gpt-4": {"input": 0.03, "output": 0.06},
      "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    },
    "claude": {
      "opus": {"input": 15.0, "output": 75.0},
      "sonnet": {"input": 3.0, "output": 15.0}
    }
  },
  "models_by_provider": {
    "openai": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
    "claude": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
  }
}
```

---

## Providers & Models

### OpenAI

**Supported Models**:
- `gpt-4` - Most capable, highest cost
- `gpt-4-turbo-preview` - Better balance of capability and cost
- `gpt-3.5-turbo` - Fast, cheapest option

**Pricing** (per 1K tokens):
- GPT-4: $0.03 input, $0.06 output
- GPT-4 Turbo: $0.01 input, $0.03 output
- GPT-3.5: $0.0005 input, $0.0015 output

### Claude (Anthropic)

**Supported Models**:
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fast and cheap

**Pricing** (per 1M tokens):
- Opus: $15 input, $75 output
- Sonnet: $3 input, $15 output
- Haiku: $0.25 input, $1.25 output

---

## Caching System

### In-Memory Cache

Used by default for single-process deployments.

**Features**:
- TTL-based expiration (default 1 hour)
- Configurable size (default 1000 items)
- Hit rate tracking
- Fast access (no network overhead)

**Example**:
```python
from app.llm import InMemoryCacheManager

cache = InMemoryCacheManager(max_size=1000, default_ttl=3600)
```

### Redis Cache

For multi-process and distributed deployments.

**Features**:
- Shared across processes
- Persistent cache
- Fine-grained TTL control

**Setup**:
```python
from app.llm import RedisCacheManager

cache = RedisCacheManager(
    redis_url="redis://localhost:6379",
    default_ttl=3600
)
```

### Cache Key Generation

Cache keys are generated from:
- LLM provider name
- Model name
- Prompt text
- Temperature parameter

```python
from app.llm import generate_cache_key

key = generate_cache_key(
    provider="openai",
    model="gpt-4",
    prompt="Your prompt here",
    temperature=0.7
)
```

---

## Cost Tracking

### Track API Costs

```python
from app.llm import CostTracker

tracker = CostTracker()

# Record a cost
record = await tracker.record_cost(
    provider="openai",
    model="gpt-4",
    input_tokens=100,
    output_tokens=50,
    cost=0.006,
    user_id="user-123",
    operation="extract_skills"
)
```

### Get Cost Statistics

```python
# Total cost
total = tracker.get_total_cost()

# Cost by provider
by_provider = tracker.get_cost_by_provider()

# Cost by model
by_model = tracker.get_cost_by_model()

# Cost by user
by_user = tracker.get_cost_by_user()

# Comprehensive stats
stats = tracker.get_stats()
```

### Forecast Costs

```python
# Estimate costs for 100 daily requests over 30 days
forecast = tracker.get_usage_forecast(
    daily_requests=100,
    days=30
)
print(f"Projected cost: ${forecast['projected_total_cost']}")
```

---

## Fallback Extraction

When LLM is unavailable, the system automatically falls back to rule-based extraction.

### Features

- 100+ predefined skills database
- Skill aliases and variations
- Case-insensitive matching
- Cloud provider detection
- Database system detection
- Framework detection
- Skill categorization

### Example Usage

```python
from app.llm import FallbackExtractor

text = "I know Python, Django, PostgreSQL, Docker, and AWS"

# Basic extraction
skills = FallbackExtractor.extract_skills(text)
# Returns: ["python", "django", "postgresql", "docker", "aws"]

# With confidence scores
with_confidence = FallbackExtractor.extract_skills_with_confidence(text)
# Returns: {"python": 0.95, "django": 0.85, ...}

# By category
by_category = FallbackExtractor.extract_skills_by_category(text)
# Returns: {
#   "programming_languages": ["python"],
#   "frameworks": ["django"],
#   "databases": ["postgresql"],
#   "tools": ["docker"],
#   "cloud_providers": ["aws"]
# }
```

---

## Error Handling

### API Failures

All API errors are logged and handled gracefully:

```python
try:
    response = await llm_provider.generate_text(prompt)
except RateLimitError:
    # Handle rate limiting
    logger.error("API rate limit exceeded")
except APIError as e:
    # Handle other API errors
    logger.error(f"API error: {e}")
```

### Automatic Fallback

When LLM fails and fallback is enabled:

```python
response = await llm_manager.extract_skills(
    text=text,
    use_fallback=True  # Automatically use fallback on error
)
```

---

## Testing

### Run Tests

```bash
# Unit tests
pytest tests/unit/test_llm_providers.py -v

# Integration tests  
pytest tests/integration/test_llm_endpoints.py -v

# All LLM tests
pytest tests/ -k llm -v

# With coverage
pytest tests/ -k llm --cov=app.llm --cov-report=html
```

### Test Coverage

**Unit Tests** (40+ test cases):
- Cache manager operations (get, set, delete, clear)
- Cost tracking and calculations
- Fallback extraction with confidence
- Provider pricing calculations
- Cache key generation and uniqueness

**Integration Tests** (25+ test cases):
- Skill extraction endpoint
- Skill extraction with confidence
- Categorized extraction
- Text generation
- Provider validation
- Metrics endpoints
- Cache control
- Authentication required for all endpoints

---

## Performance Considerations

### Caching Impact

- Cache hits: ~1ms response time
- Cache misses: 100-500ms (depends on LLM)
- Hit rate: Typically 60-80% for repeated queries

### Cost Optimization

```python
# Use cheaper models when possible
response = await manager.extract_skills(
    text=text,
    provider=LLMProvider.OPENAI,
    model="gpt-3.5-turbo",  # Cheaper than gpt-4
    use_cache=True  # Reuse cached results
)

# Monitor costs
metrics = manager.get_metrics()
print(f"Total cost: ${metrics['cost_stats']['total_cost']}")
```

### Token Usage

- Skill extraction: Typically 20-100 tokens input, 10-50 tokens output
- Text generation: Varies by prompt length and max_tokens

### Rate Limiting

Be mindful of API rate limits:
- OpenAI GPT-3.5: 3,500 RPM
- OpenAI GPT-4: 200 RPM
- Claude: Varies by tier

---

## Troubleshooting

### Provider Not Available

```json
{
  "error": "Provider openai not available",
  "solution": "Set OPENAI_API_KEY environment variable"
}
```

### Cache Miss Providing Fallback

If cache misses frequently:
1. Increase cache size: `InMemoryCacheManager(max_size=5000)`
2. Use Redis for larger capacity
3. Increase TTL: `default_ttl=7200` (2 hours)

### High Costs

1. Check cost statistics: `GET /api/llm/costs/stats`
2. Review by model: Look for expensive models (gpt-4)
3. Forecast: `GET /api/llm/costs/forecast`
4. Switch to cheaper models
5. Increase cache effectiveness

### API Rate Limiting

If receiving 429 errors:
1. Implement exponential backoff
2. Use cheaper models with higher limits
3. Request rate limit increase from provider
4. Spread requests over time

---

## Best Practices

### 1. Always Use Caching
```python
await manager.extract_skills(
    text=text,
    use_cache=True  # ✓ Good
)
```

### 2. Enable Fallback
```python
await manager.extract_skills(
    text=text,
    use_fallback=True  # ✓ Provides resilience
)
```

### 3. Monitor Costs
```python
forecast = manager.cost_tracker.get_usage_forecast(
    daily_requests=100,
    days=30
)
print(f"Monthly cost estimate: ${forecast['projected_monthly_cost']}")
```

### 4. Validate Providers
```python
results = await manager.validate_providers()
for provider, is_valid in results.items():
    if not is_valid:
        logger.warning(f"Provider {provider} is not responding")
```

### 5. Use Appropriate Models
- Simple tasks: Use `gpt-3.5-turbo` (fastest, cheapest)
- Complex tasks: Use `gpt-4` or `claude-3-opus`
- Balanced: Use `gpt-4-turbo` or `claude-3-sonnet`

---

## Integration Examples

### Integrate with Skill Extraction Service

```python
# In app/services/skill_extractor.py
class SkillExtractor:
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
    
    async def extract_skills(self, text: str) -> List[str]:
        # Try LLM first
        response = await self.llm_manager.extract_skills(
            text=text,
            use_fallback=True
        )
        return response.metadata["skills"]
```

### Track Skills by User

```python
# Record extraction for cost attribution
await manager.extract_skills(
    text=text,
    user_id=user.id,  # Track per user
)

# Analyze user costs
user_costs = manager.cost_tracker.get_cost_by_user()
for user_id, cost in user_costs.items():
    print(f"User {user_id}: ${cost}")
```

---

## Migration Notes

This phase integrates with existing components:

✅ **Existing Skill Extraction**: Enhanced with LLM capabilities
✅ **Auth System**: All endpoints require authentication
✅ **Logging**: All API calls are logged
✅ **Monitoring**: Metrics available via /api/v1/metrics

No breaking changes to existing APIs.

---

## Summary Statistics

**Phase 6 Deliverables**:
- 8 modules (2,600+ LOC)
- 11 API endpoints
- 65+ test cases
- Support for 2 major LLM providers
- Flexible caching (in-memory + Redis)
- Cost tracking and forecasting
- Rule-based fallback system
- Full error handling and resilience

**Next Steps**:
1. Configure API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
2. Run tests: `pytest tests/ -k llm -v`
3. Monitor costs: `GET /api/llm/costs/stats`
4. Integrate with your application
5. Set up cost alerts and monitoring
