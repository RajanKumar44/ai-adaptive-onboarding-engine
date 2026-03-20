"""
Advanced Search Functionality

Provides comprehensive search capabilities including:
- Full-text search across multiple fields
- Field-specific search
- Search ranking and relevance scoring
- Search query building and execution
"""

from typing import List, Optional, Dict, Tuple, Any, Type
from enum import Enum
from sqlalchemy import Column, or_, and_, func
from sqlalchemy.orm import Query
from datetime import datetime
import re


class SearchMode(str, Enum):
    """Search mode enumeration"""
    SIMPLE = "simple"          # Simple substring match
    PHRASE = "phrase"          # Exact phrase match
    BOOLEAN = "boolean"        # Boolean search (AND/OR/NOT)
    FUZZY = "fuzzy"            # Fuzzy matching (not exact)
    REGEX = "regex"            # Regular expression


class SearchField:
    """Represents a searchable field with weight and type"""
    
    def __init__(
        self,
        column: Column,
        weight: float = 1.0,
        searchable: bool = True,
        analyzer: Optional[str] = None
    ):
        """
        Initialize search field
        
        Args:
            column: SQLAlchemy column
            weight: Relevance weight (higher = more relevant)
            searchable: Whether this field is searchable
            analyzer: Text analyzer type (simple, whitespace, stopword)
        """
        self.column = column
        self.weight = weight
        self.searchable = searchable
        self.analyzer = analyzer or "simple"
    
    def get_search_expression(self, query: str, mode: SearchMode):
        """Build search expression for this field"""
        if mode == SearchMode.SIMPLE:
            return self.column.ilike(f"%{query}%")
        elif mode == SearchMode.PHRASE:
            return self.column.ilike(f"%{query}%")
        elif mode == SearchMode.REGEX:
            # Basic regex support via ilike (limited)
            return self.column.regexp_match(query) if hasattr(self.column, 'regexp_match') else None
        else:
            return self.column.ilike(f"%{query}%")


class SearchBuilder:
    """
    Builds and executes search queries
    
    Usage:
        builder = SearchBuilder()
        builder.add_field(User.name, weight=2.0)
        builder.add_field(User.email, weight=1.5)
        builder.add_field(User.bio)
        
        results = builder.search("john", mode=SearchMode.SIMPLE)
    """
    
    def __init__(self):
        """Initialize search builder"""
        self.fields: List[SearchField] = []
        self._weights: Dict[str, float] = {}
    
    def add_field(
        self,
        column: Column,
        weight: float = 1.0,
        searchable: bool = True,
        analyzer: str = "simple"
    ) -> "SearchBuilder":
        """Add a searchable field"""
        field = SearchField(column, weight, searchable, analyzer)
        if searchable:
            self.fields.append(field)
            self._weights[str(column)] = weight
        return self
    
    def add_fields(self, field_definitions: List[Tuple[Column, float]]) -> "SearchBuilder":
        """Add multiple fields"""
        for column, weight in field_definitions:
            self.add_field(column, weight)
        return self
    
    def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.SIMPLE,
        session=None,
        model: Type = None
    ) -> List[Any]:
        """
        Execute search
        
        Args:
            query: Search query string
            mode: Search mode
            session: SQLAlchemy session (optional, for direct execution)
            model: Model class (required if session provided)
            
        Returns:
            List of matching records
        """
        if not self.fields:
            return []
        
        # Clean query
        query = self._clean_query(query)
        if not query:
            return []
        
        # Build search expression
        expressions = []
        for field in self.fields:
            expr = field.get_search_expression(query, mode)
            if expr is not None:
                expressions.append(expr)
        
        if not expressions:
            return []
        
        # Return query builder (expression)
        return or_(*expressions)
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize search query"""
        if not query:
            return ""
        # Remove special characters except spaces, *, ", -
        query = re.sub(r'[^\w\s\*\"-]', '', query)
        query = query.strip()
        return query


class FullTextSearchEngine:
    """
    Full-text search engine for complex queries
    
    Usage:
        engine = FullTextSearchEngine(User)
        engine.add_field(User.name, weight=2.0)
        engine.add_field(User.email)
        engine.add_field(User.bio)
        
        results = engine.search("python developer", session=db)
    """
    
    def __init__(self, model: Type):
        """Initialize search engine"""
        self.model = model
        self.builder = SearchBuilder()
    
    def add_field(
        self,
        column: Column,
        weight: float = 1.0
    ) -> "FullTextSearchEngine":
        """Add searchable field"""
        self.builder.add_field(column, weight)
        return self
    
    def add_fields(self, field_defs: List[Tuple[Column, float]]) -> "FullTextSearchEngine":
        """Add multiple searchable fields"""
        self.builder.add_fields(field_defs)
        return self
    
    def search(
        self,
        query: str,
        session,
        mode: SearchMode = SearchMode.SIMPLE,
        limit: int = 50,
        skip: int = 0
    ) -> Tuple[List[Any], int]:
        """
        Execute full-text search with pagination
        
        Args:
            query: Search query
            session: SQLAlchemy session
            mode: Search mode
            limit: Max results
            skip: Skip count
            
        Returns:
            Tuple of (results, total_count)
        """
        search_expr = self.builder.search(query, mode, session, self.model)
        
        q = session.query(self.model)
        
        if search_expr is not None:
            q = q.filter(search_expr)
        
        total = q.count()
        results = q.offset(skip).limit(limit).all()
        
        return results, total
    
    def search_by_fields(
        self,
        field_queries: Dict[str, str],
        session,
        limit: int = 50,
        skip: int = 0,
        match_all: bool = False
    ) -> Tuple[List[Any], int]:
        """
        Search with different queries for different fields
        
        Args:
            field_queries: Dict of {field_name: query}
            session: SQLAlchemy session
            limit: Max results
            skip: Skip count
            match_all: If True, all conditions must match (AND), else any (OR)
            
        Returns:
            Tuple of (results, total_count)
        """
        expressions = []
        
        for field, query_str in field_queries.items():
            try:
                column = getattr(self.model, field)
                expressions.append(column.ilike(f"%{query_str}%"))
            except AttributeError:
                continue
        
        if not expressions:
            return [], 0
        
        q = session.query(self.model)
        
        if match_all:
            q = q.filter(and_(*expressions))
        else:
            q = q.filter(or_(*expressions))
        
        total = q.count()
        results = q.offset(skip).limit(limit).all()
        
        return results, total


class SearchHighlighter:
    """Highlights search matches in results"""
    
    def __init__(self, highlight_tag: str = "em"):
        """
        Initialize highlighter
        
        Args:
            highlight_tag: HTML tag to wrap matches (em, strong, mark, etc.)
        """
        self.highlight_tag = highlight_tag
    
    def highlight(self, text: str, query: str, case_sensitive: bool = False) -> str:
        """
        Highlight query terms in text
        
        Args:
            text: Text to highlight
            query: Query string to highlight
            case_sensitive: Whether matching is case sensitive
            
        Returns:
            Text with highlighted matches
        """
        if not text or not query:
            return text
        
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = r'\b' + re.escape(query) + r'\b'
        
        replacement = f'<{self.highlight_tag}>\\g<0></{self.highlight_tag}>'
        return re.sub(pattern, replacement, text, flags=flags)
    
    def highlight_multiple(
        self,
        text: str,
        queries: List[str],
        case_sensitive: bool = False
    ) -> str:
        """Highlight multiple query terms"""
        for query in queries:
            text = self.highlight(text, query, case_sensitive)
        return text


class SearchResult:
    """Represents a search result with metadata"""
    
    def __init__(
        self,
        record: Any,
        relevance_score: float = 1.0,
        highlights: Optional[Dict[str, str]] = None
    ):
        """
        Initialize search result
        
        Args:
            record: The actual record
            relevance_score: Relevance score (0-1)
            highlights: Dict of field names to highlighted text
        """
        self.record = record
        self.relevance_score = relevance_score
        self.highlights = highlights or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record": self.record,
            "relevance_score": self.relevance_score,
            "highlights": self.highlights
        }


class SearchRelevanceRanker:
    """Ranks search results by relevance"""
    
    def __init__(self):
        """Initialize ranker"""
        self.field_weights: Dict[str, float] = {}
    
    def set_field_weight(self, field: str, weight: float) -> "SearchRelevanceRanker":
        """Set weight for a field"""
        self.field_weights[field] = weight
        return self
    
    def rank(
        self,
        results: List[Any],
        query: str,
        field_getters: Dict[str, callable]
    ) -> List[SearchResult]:
        """
        Rank results by relevance
        
        Args:
            results: List of records
            query: Search query
            field_getters: Dict of {field_name: getter_function}
            
        Returns:
            Sorted list of SearchResult objects
        """
        ranked = []
        query_terms = query.lower().split()
        
        for record in results:
            score = 0.0
            highlights = {}
            
            for field, getter in field_getters.items():
                try:
                    value = getter(record)
                    if not value:
                        continue
                    
                    value_str = str(value).lower()
                    weight = self.field_weights.get(field, 1.0)
                    
                    # Score based on query term matches
                    matches = sum(1 for term in query_terms if term in value_str)
                    score += matches * weight
                    
                    # Highlight matches
                    if matches > 0:
                        highlighter = SearchHighlighter()
                        highlights[field] = highlighter.highlight_multiple(
                            str(value),
                            query_terms
                        )
                
                except Exception:
                    continue
            
            # Normalize score
            if score > 0:
                ranked.append(SearchResult(record, score, highlights))
        
        # Sort by relevance score (descending)
        ranked.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked
