"""
Advanced Filtering and Sorting Utilities

Provides comprehensive filtering and sorting support for database queries with:
- Dynamic filter builders
- Multi-field sorting
- Filter chain composition
- SQLAlchemy integration
"""

from typing import List, Optional, Dict, Any, Type
from enum import Enum
from sqlalchemy import Column, and_, or_
from sqlalchemy.orm import Query
from pydantic import BaseModel, Field


class FilterOperator(str, Enum):
    """Filter operator enumeration"""
    EQ = "eq"           # Equals
    NE = "ne"           # Not equals
    GT = "gt"           # Greater than
    GTE = "gte"        # Greater than or equal
    LT = "lt"          # Less than
    LTE = "lte"        # Less than or equal
    LIKE = "like"      # String contains
    IN = "in"          # Value in list
    BETWEEN = "between"  # Between two values
    IS_NULL = "is_null"  # Is null
    
    def __str__(self):
        return self.value


class SortDirection(str, Enum):
    """Sort direction enumeration"""
    ASC = "asc"
    DESC = "desc"
    
    def __str__(self):
        return self.value


class FilterRule(BaseModel):
    """Individual filter rule"""
    
    field: str = Field(description="Database field name")
    operator: FilterOperator = Field(description="Filter operator")
    value: Optional[Any] = Field(default=None, description="Filter value")
    
    class Config:
        use_enum_values = True


class SortRule(BaseModel):
    """Individual sort rule"""
    
    field: str = Field(description="Database field name")
    direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")
    
    class Config:
        use_enum_values = True


class FilterBuilder:
    """
    Builds dynamic SQLAlchemy filters from rule definitions
    
    Usage:
        builder = FilterBuilder()
        builder.add_filter("status", FilterOperator.EQ, "active")
        builder.add_filter("created_at", FilterOperator.GT, start_date)
        filters = builder.build()
        query = session.query(User).filter(filters)
    """
    
    def __init__(self, logical_op: str = "and"):
        """
        Initialize filter builder
        
        Args:
            logical_op: "and" or "or" - determines how filters are combined
        """
        self.rules: List[FilterRule] = []
        self.logical_op = logical_op.lower()
        if self.logical_op not in ("and", "or"):
            self.logical_op = "and"
    
    def add_filter(
        self,
        field: str,
        operator: FilterOperator,
        value: Any = None
    ) -> "FilterBuilder":
        """Add a filter rule"""
        self.rules.append(FilterRule(field=field, operator=operator, value=value))
        return self  # Enable chaining
    
    def add_filters(self, filters: List[FilterRule]) -> "FilterBuilder":
        """Add multiple filter rules"""
        self.rules.extend(filters)
        return self  # Enable chaining
    
    def clear(self) -> "FilterBuilder":
        """Clear all rules"""
        self.rules = []
        return self
    
    def build(self, model: Type) -> Optional[Any]:
        """
        Build SQLAlchemy filter expression from rules
        
        Args:
            model: SQLAlchemy model class
            
        Returns:
            SQLAlchemy filter expression or None if no rules
        """
        if not self.rules:
            return None
        
        expressions = []
        for rule in self.rules:
            expr = self._build_expression(model, rule)
            if expr is not None:
                expressions.append(expr)
        
        if not expressions:
            return None
        
        if self.logical_op == "or":
            return or_(*expressions)
        else:
            return and_(*expressions)
    
    @staticmethod
    def _build_expression(model: Type, rule: FilterRule) -> Optional[Any]:
        """Build individual filter expression"""
        try:
            field = getattr(model, rule.field)
        except AttributeError:
            return None  # Field doesn't exist on model
        
        operator = rule.operator
        value = rule.value
        
        if operator == FilterOperator.EQ:
            return field == value
        elif operator == FilterOperator.NE:
            return field != value
        elif operator == FilterOperator.GT:
            return field > value
        elif operator == FilterOperator.GTE:
            return field >= value
        elif operator == FilterOperator.LT:
            return field < value
        elif operator == FilterOperator.LTE:
            return field <= value
        elif operator == FilterOperator.LIKE:
            return field.ilike(f"%{value}%")
        elif operator == FilterOperator.IN:
            if isinstance(value, (list, tuple)):
                return field.in_(value)
            return None
        elif operator == FilterOperator.BETWEEN:
            if isinstance(value, (list, tuple)) and len(value) == 2:
                return field.between(value[0], value[1])
            return None
        elif operator == FilterOperator.IS_NULL:
            if value:
                return field.is_(None)
            else:
                return field.isnot(None)
        
        return None


class SortBuilder:
    """
    Builds dynamic SQLAlchemy sort expressions
    
    Usage:
        builder = SortBuilder()
        builder.add_sort("created_at", SortDirection.DESC)
        builder.add_sort("name", SortDirection.ASC)
        query = session.query(User)
        query = builder.apply(query, User)
    """
    
    def __init__(self):
        """Initialize sort builder"""
        self.rules: List[SortRule] = []
    
    def add_sort(
        self,
        field: str,
        direction: SortDirection = SortDirection.ASC
    ) -> "SortBuilder":
        """Add a sort rule"""
        self.rules.append(SortRule(field=field, direction=direction))
        return self  # Enable chaining
    
    def add_sorts(self, sorts: List[SortRule]) -> "SortBuilder":
        """Add multiple sort rules"""
        self.rules.extend(sorts)
        return self  # Enable chaining
    
    def clear(self) -> "SortBuilder":
        """Clear all rules"""
        self.rules = []
        return self
    
    def apply(self, query: Query, model: Type) -> Query:
        """Apply sort rules to query"""
        for rule in self.rules:
            try:
                field = getattr(model, rule.field)
                if rule.direction == SortDirection.DESC:
                    query = query.order_by(field.desc())
                else:
                    query = query.order_by(field.asc())
            except AttributeError:
                continue  # Skip invalid fields
        
        return query


class QueryFilter:
    """
    Combines filtering, sorting, and pagination into a single interface
    
    Usage:
        qf = QueryFilter()
        qf.add_filter("status", FilterOperator.EQ, "active")
        qf.add_sort("created_at", SortDirection.DESC)
        qf.set_pagination(skip=0, limit=10)
        
        results, total = qf.execute(session, User)
    """
    
    def __init__(self):
        """Initialize query filter"""
        self.filter_builder = FilterBuilder()
        self.sort_builder = SortBuilder()
        self.skip = 0
        self.limit = 10
    
    def add_filter(
        self,
        field: str,
        operator: FilterOperator,
        value: Any = None
    ) -> "QueryFilter":
        """Add a filter"""
        self.filter_builder.add_filter(field, operator, value)
        return self
    
    def add_sort(
        self,
        field: str,
        direction: SortDirection = SortDirection.ASC
    ) -> "QueryFilter":
        """Add a sort"""
        self.sort_builder.add_sort(field, direction)
        return self
    
    def set_pagination(self, skip: int = 0, limit: int = 10) -> "QueryFilter":
        """Set pagination parameters"""
        self.skip = max(0, skip)
        self.limit = max(1, min(limit, 100))  # Limit to 100
        return self
    
    def execute(self, session, model: Type, count_all: bool = True):
        """
        Execute query with filters, sorts, and pagination
        
        Args:
            session: SQLAlchemy session
            model: Model class
            count_all: Whether to count total records
            
        Returns:
            Tuple of (results, total_count)
        """
        query = session.query(model)
        
        # Apply filters
        filters = self.filter_builder.build(model)
        if filters is not None:
            query = query.filter(filters)
        
        # Get total before pagination
        total = query.count() if count_all else None
        
        # Apply sorting
        query = self.sort_builder.apply(query, model)
        
        # Apply pagination
        query = query.offset(self.skip).limit(self.limit)
        
        return query.all(), total


class FilterChain:
    """
    Chainable filter composition for complex queries
    
    Usage:
        chain = FilterChain(model)
        chain.where("status", FilterOperator.EQ, "active") \
            .where("age", FilterOperator.GTE, 18) \
            .sort_by("created_at", SortDirection.DESC) \
            .limit(10)
        
        results = chain.execute(session)
    """
    
    def __init__(self, model: Type):
        """Initialize filter chain"""
        self.model = model
        self.qf = QueryFilter()
    
    def where(
        self,
        field: str,
        operator: FilterOperator,
        value: Any = None
    ) -> "FilterChain":
        """Add WHERE clause"""
        self.qf.add_filter(field, operator, value)
        return self
    
    def sort_by(
        self,
        field: str,
        direction: SortDirection = SortDirection.ASC
    ) -> "FilterChain":
        """Add ORDER BY clause"""
        self.qf.add_sort(field, direction)
        return self
    
    def limit(self, limit: int) -> "FilterChain":
        """Set result limit"""
        self.qf.limit = max(1, min(limit, 100))
        return self
    
    def offset(self, skip: int) -> "FilterChain":
        """Set result offset"""
        self.qf.skip = max(0, skip)
        return self
    
    def execute(self, session):
        """Execute the filter chain"""
        return self.qf.execute(session, self.model)


class ValidFieldChecker:
    """Validates filter/sort fields against model"""
    
    def __init__(self, model: Type):
        """Initialize with model"""
        self.model = model
        self.valid_fields = self._get_valid_fields()
    
    def _get_valid_fields(self) -> set:
        """Get all valid field names from model"""
        return {col.name for col in self.model.__table__.columns}
    
    def is_valid(self, field: str) -> bool:
        """Check if field is valid"""
        return field in self.valid_fields
    
    def filter_valid_fields(self, fields: List[str]) -> List[str]:
        """Filter to only valid fields"""
        return [f for f in fields if self.is_valid(f)]
