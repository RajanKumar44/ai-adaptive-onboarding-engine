"""
LLM API cost tracking and monitoring system.
Tracks costs across providers and models.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy import Column, String, Float, Integer, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


@dataclass
class CostRecord:
    """Individual API call cost record."""
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    timestamp: datetime
    request_id: str = None
    user_id: str = None
    operation: str = "generate_text"  # generate_text, extract_skills, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CostTracker:
    """
    Tracks LLM API costs across providers and models.
    Supports both in-memory and database persistence.
    """
    
    def __init__(self, database_url: str = None, use_persistence: bool = False):
        """
        Initialize cost tracker.
        
        Args:
            database_url: Optional database URL for persistence
            use_persistence: Whether to persist costs to database
        """
        self.in_memory_costs: List[CostRecord] = []
        self.use_persistence = use_persistence
        self.db_session = None
        
        if use_persistence and database_url:
            try:
                engine = create_engine(database_url)
                Base.metadata.create_all(engine)
                Session = sessionmaker(bind=engine)
                self.db_session = Session()
                logger.info("Cost tracking database initialized")
            except Exception as e:
                logger.error(f"Failed to initialize cost tracking database: {str(e)}")
                self.use_persistence = False
    
    async def record_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        request_id: str = None,
        user_id: str = None,
        operation: str = "generate_text"
    ) -> CostRecord:
        """
        Record an API call cost.
        
        Args:
            provider: LLM provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Cost in USD
            request_id: Optional request ID for tracking
            user_id: Optional user ID
            operation: Operation type
            
        Returns:
            CostRecord created
        """
        total_tokens = input_tokens + output_tokens
        
        record = CostRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            timestamp=datetime.utcnow(),
            request_id=request_id,
            user_id=user_id,
            operation=operation,
        )
        
        # Store in memory
        self.in_memory_costs.append(record)
        
        # Persist if enabled
        if self.use_persistence and self.db_session:
            try:
                # Here you would insert into database table
                # For now, we just log
                logger.debug(
                    f"Cost recorded: {provider}/{model} - "
                    f"{total_tokens} tokens - ${cost:.6f}"
                )
            except Exception as e:
                logger.error(f"Failed to persist cost record: {str(e)}")
        
        logger.info(
            f"Cost recorded",
            extra={
                "provider": provider,
                "model": model,
                "tokens": total_tokens,
                "cost": cost,
                "user_id": user_id,
            }
        )
        
        return record
    
    def get_costs(
        self,
        provider: str = None,
        model: str = None,
        user_id: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> List[CostRecord]:
        """
        Get cost records with optional filtering.
        
        Args:
            provider: Filter by provider
            model: Filter by model
            user_id: Filter by user
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of matching CostRecords
        """
        records = self.in_memory_costs
        
        if provider:
            records = [r for r in records if r.provider == provider]
        
        if model:
            records = [r for r in records if r.model == model]
        
        if user_id:
            records = [r for r in records if r.user_id == user_id]
        
        if start_time:
            records = [r for r in records if r.timestamp >= start_time]
        
        if end_time:
            records = [r for r in records if r.timestamp <= end_time]
        
        return records
    
    def get_total_cost(
        self,
        provider: str = None,
        model: str = None,
        user_id: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> float:
        """
        Get total cost for filtered records.
        
        Args:
            provider: Filter by provider
            model: Filter by model
            user_id: Filter by user
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Total cost in USD
        """
        records = self.get_costs(provider, model, user_id, start_time, end_time)
        return round(sum(r.cost for r in records), 4)
    
    def get_cost_by_provider(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> Dict[str, float]:
        """
        Get costs grouped by provider.
        
        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Dictionary mapping provider to total cost
        """
        records = self.get_costs(start_time=start_time, end_time=end_time)
        costs = {}
        
        for record in records:
            if record.provider not in costs:
                costs[record.provider] = 0.0
            costs[record.provider] += record.cost
        
        return {k: round(v, 4) for k, v in costs.items()}
    
    def get_cost_by_model(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> Dict[str, float]:
        """
        Get costs grouped by model.
        
        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Dictionary mapping model to total cost
        """
        records = self.get_costs(start_time=start_time, end_time=end_time)
        costs = {}
        
        for record in records:
            if record.model not in costs:
                costs[record.model] = 0.0
            costs[record.model] += record.cost
        
        return {k: round(v, 4) for k, v in costs.items()}
    
    def get_cost_by_user(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> Dict[str, float]:
        """
        Get costs grouped by user.
        
        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Dictionary mapping user_id to total cost
        """
        records = self.get_costs(start_time=start_time, end_time=end_time)
        costs = {}
        
        for record in records:
            if record.user_id:
                if record.user_id not in costs:
                    costs[record.user_id] = 0.0
                costs[record.user_id] += record.cost
        
        return {k: round(v, 4) for k, v in costs.items()}
    
    def get_stats(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive cost statistics.
        
        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Dictionary with cost statistics
        """
        records = self.get_costs(start_time=start_time, end_time=end_time)
        
        if not records:
            return {"error": "No cost records found"}
        
        total_cost = sum(r.cost for r in records)
        total_tokens = sum(r.total_tokens for r in records)
        total_input_tokens = sum(r.input_tokens for r in records)
        total_output_tokens = sum(r.output_tokens for r in records)
        
        return {
            "total_requests": len(records),
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "avg_cost_per_request": round(total_cost / len(records), 6),
            "avg_tokens_per_request": round(total_tokens / len(records), 1),
            "cost_by_provider": self.get_cost_by_provider(start_time, end_time),
            "cost_by_model": self.get_cost_by_model(start_time, end_time),
            "cost_by_user": self.get_cost_by_user(start_time, end_time),
            "details": [r.to_dict() for r in records[-10:]],  # Last 10 records
        }
    
    def get_usage_forecast(
        self,
        daily_requests: int = 100,
        days: int = 30,
        avg_cost_per_request: float = None
    ) -> Dict[str, Any]:
        """
        Forecast future LLM usage costs.
        
        Args:
            daily_requests: Expected requests per day
            days: Number of days to forecast
            avg_cost_per_request: Average cost per request (uses historical if None)
            
        Returns:
            Dictionary with cost forecast
        """
        records = self.in_memory_costs
        
        if not records and not avg_cost_per_request:
            return {"error": "No historical data for forecast"}
        
        if avg_cost_per_request is None:
            avg_cost_per_request = (
                sum(r.cost for r in records) / len(records)
            )
        
        total_requests = daily_requests * days
        projected_cost = total_requests * avg_cost_per_request
        
        return {
            "daily_requests": daily_requests,
            "forecast_days": days,
            "total_projected_requests": total_requests,
            "avg_cost_per_request": round(avg_cost_per_request, 6),
            "projected_total_cost": round(projected_cost, 2),
            "projected_monthly_cost": round(
                (daily_requests * 30 * avg_cost_per_request), 2
            ),
        }
    
    def clear_costs(self):
        """Clear all cost records (use carefully in production)."""
        self.in_memory_costs = []
        logger.warning("All cost records cleared")
