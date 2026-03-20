"""
Bulk Operations Handler

Provides comprehensive bulk operation support including:
- Batch create operations
- Batch update operations
- Batch delete operations
- Transaction management
- Error handling and rollback
"""

from typing import List, Dict, Any, Type, Optional, Tuple
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class BulkOperationType(str, Enum):
    """Bulk operation type enumeration"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"


class BulkItemStatus(str, Enum):
    """Status of individual bulk operation item"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class BulkOperationRequest(BaseModel):
    """Request for bulk operation"""
    
    operation: BulkOperationType = Field(description="Type of bulk operation")
    items: List[Dict[str, Any]] = Field(description="List of items to operate on")
    atomic: bool = Field(
        default=True,
        description="If True, all-or-nothing; if False, partial success allowed"
    )
    
    class Config:
        use_enum_values = True


class BulkOperationItemResult(BaseModel):
    """Result of individual bulk operation item"""
    
    index: int = Field(description="Index of item in request")
    status: BulkItemStatus = Field(description="Status of operation")
    success: bool = Field(description="Whether operation succeeded")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Resulting data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_type: Optional[str] = Field(default=None, description="Type of error")
    
    class Config:
        use_enum_values = True


class BulkOperationResult(BaseModel):
    """Result of entire bulk operation"""
    
    operation: BulkOperationType = Field(description="Operation type")
    total_items: int = Field(description="Total items requested")
    successful_items: int = Field(description="Number of successful operations")
    failed_items: int = Field(description="Number of failed operations")
    items: List[BulkOperationItemResult] = Field(description="Results for each item")
    duration_ms: float = Field(description="Duration in milliseconds")
    success_rate: float = Field(description="Success rate (0-1)")
    started_at: datetime = Field(description="When operation started")
    completed_at: datetime = Field(description="When operation completed")
    errors_summary: List[str] = Field(default_factory=list, description="Summary of errors")
    
    class Config:
        use_enum_values = True


class BulkOperationHandler:
    """
    Handles bulk operations on database models
    
    Usage:
        handler = BulkOperationHandler()
        
        # Bulk create
        items = [{"name": "John"}, {"name": "Jane"}]
        result = handler.bulk_create(session, User, items)
        
        # Bulk update
        items = [
            {"id": 1, "name": "John Updated"},
            {"id": 2, "name": "Jane Updated"}
        ]
        result = handler.bulk_update(session, User, items, key_field="id")
        
        # Bulk delete
        ids = [1, 2, 3]
        result = handler.bulk_delete(session, User, ids, key_field="id")
    """
    
    def __init__(self, batch_size: int = 100):
        """
        Initialize handler
        
        Args:
            batch_size: Size of batches for processing
        """
        self.batch_size = max(1, batch_size)
    
    def bulk_create(
        self,
        session: Session,
        model: Type,
        items: List[Dict[str, Any]],
        atomic: bool = True
    ) -> BulkOperationResult:
        """
        Bulk create items
        
        Args:
            session: SQLAlchemy session
            model: Model class
            items: List of dictionaries to create
            atomic: All-or-nothing operation
            
        Returns:
            BulkOperationResult with status of each item
        """
        start_time = datetime.utcnow()
        item_results = []
        created_objects = []
        
        for index, item_data in enumerate(items):
            try:
                # Create model instance
                obj = model(**item_data)
                session.add(obj)
                created_objects.append((index, obj))
                
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.PENDING,
                    success=True,
                    data=item_data
                ))
            except Exception as e:
                logger.error(f"Bulk create error at index {index}: {str(e)}")
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.FAILED,
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__
                ))
        
        # Commit
        try:
            session.commit()
            # Update pending items to success
            for item_result in item_results:
                if item_result.status == BulkItemStatus.PENDING:
                    item_result.status = BulkItemStatus.SUCCESS
        except SQLAlchemyError as e:
            logger.error(f"Bulk create commit error: {str(e)}")
            session.rollback()
            
            if atomic:
                # Mark all as failed
                for item_result in item_results:
                    if item_result.status == BulkItemStatus.PENDING:
                        item_result.status = BulkItemStatus.FAILED
                        item_result.success = False
                        item_result.error = str(e)
                        item_result.error_type = type(e).__name__
            else:
                # Keep partial success
                for item_result in item_results:
                    if item_result.status == BulkItemStatus.PENDING:
                        item_result.status = BulkItemStatus.PARTIAL
                        item_result.error = "Transaction rolled back"
        
        return self._build_result(
            BulkOperationType.CREATE,
            item_results,
            start_time
        )
    
    def bulk_update(
        self,
        session: Session,
        model: Type,
        items: List[Dict[str, Any]],
        key_field: str = "id",
        atomic: bool = True
    ) -> BulkOperationResult:
        """
        Bulk update items
        
        Args:
            session: SQLAlchemy session
            model: Model class
            items: List of dictionaries to update
            key_field: Field to match on
            atomic: All-or-nothing operation
            
        Returns:
            BulkOperationResult with status of each item
        """
        start_time = datetime.utcnow()
        item_results = []
        
        for index, item_data in enumerate(items):
            try:
                key_value = item_data.get(key_field)
                if key_value is None:
                    raise ValueError(f"Missing key field: {key_field}")
                
                # Find and update
                obj = session.query(model).filter(
                    getattr(model, key_field) == key_value
                ).first()
                
                if not obj:
                    raise ValueError(f"Record not found with {key_field}={key_value}")
                
                # Update attributes
                for field, value in item_data.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
                
                session.add(obj)
                
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.PENDING,
                    success=True,
                    data=item_data
                ))
            except Exception as e:
                logger.error(f"Bulk update error at index {index}: {str(e)}")
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.FAILED,
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__
                ))
        
        # Commit
        try:
            session.commit()
            for item_result in item_results:
                if item_result.status == BulkItemStatus.PENDING:
                    item_result.status = BulkItemStatus.SUCCESS
        except SQLAlchemyError as e:
            logger.error(f"Bulk update commit error: {str(e)}")
            session.rollback()
            
            if atomic:
                for item_result in item_results:
                    if item_result.status == BulkItemStatus.PENDING:
                        item_result.status = BulkItemStatus.FAILED
                        item_result.success = False
                        item_result.error = str(e)
                        item_result.error_type = type(e).__name__
            else:
                for item_result in item_results:
                    if item_result.status == BulkItemStatus.PENDING:
                        item_result.status = BulkItemStatus.PARTIAL
                        item_result.error = "Transaction rolled back"
        
        return self._build_result(
            BulkOperationType.UPDATE,
            item_results,
            start_time
        )
    
    def bulk_delete(
        self,
        session: Session,
        model: Type,
        ids: List[Any],
        key_field: str = "id",
        atomic: bool = True
    ) -> BulkOperationResult:
        """
        Bulk delete items
        
        Args:
            session: SQLAlchemy session
            model: Model class
            ids: List of IDs to delete
            key_field: Field to match on
            atomic: All-or-nothing operation
            
        Returns:
            BulkOperationResult with status of each item
        """
        start_time = datetime.utcnow()
        item_results = []
        deleted_objects = []
        
        for index, id_value in enumerate(ids):
            try:
                obj = session.query(model).filter(
                    getattr(model, key_field) == id_value
                ).first()
                
                if not obj:
                    raise ValueError(f"Record not found with {key_field}={id_value}")
                
                session.delete(obj)
                deleted_objects.append((index, id_value))
                
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.PENDING,
                    success=True,
                    data={key_field: id_value}
                ))
            except Exception as e:
                logger.error(f"Bulk delete error at index {index}: {str(e)}")
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.FAILED,
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__
                ))
        
        # Commit
        try:
            session.commit()
            for item_result in item_results:
                if item_result.status == BulkItemStatus.PENDING:
                    item_result.status = BulkItemStatus.SUCCESS
        except SQLAlchemyError as e:
            logger.error(f"Bulk delete commit error: {str(e)}")
            session.rollback()
            
            if atomic:
                for item_result in item_results:
                    if item_result.status == BulkItemStatus.PENDING:
                        item_result.status = BulkItemStatus.FAILED
                        item_result.success = False
                        item_result.error = str(e)
                        item_result.error_type = type(e).__name__
        
        return self._build_result(
            BulkOperationType.DELETE,
            item_results,
            start_time
        )
    
    def bulk_upsert(
        self,
        session: Session,
        model: Type,
        items: List[Dict[str, Any]],
        key_field: str = "id",
        atomic: bool = True
    ) -> BulkOperationResult:
        """
        Bulk upsert (create or update) items
        
        Args:
            session: SQLAlchemy session
            model: Model class
            items: List of dictionaries
            key_field: Field to match on
            atomic: All-or-nothing operation
            
        Returns:
            BulkOperationResult with status of each item
        """
        start_time = datetime.utcnow()
        item_results = []
        
        for index, item_data in enumerate(items):
            try:
                key_value = item_data.get(key_field)
                if key_value is None:
                    raise ValueError(f"Missing key field: {key_field}")
                
                # Try to find existing
                obj = session.query(model).filter(
                    getattr(model, key_field) == key_value
                ).first()
                
                if obj:
                    # Update
                    for field, value in item_data.items():
                        if hasattr(obj, field):
                            setattr(obj, field, value)
                else:
                    # Create
                    obj = model(**item_data)
                
                session.add(obj)
                
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.PENDING,
                    success=True,
                    data=item_data
                ))
            except Exception as e:
                logger.error(f"Bulk upsert error at index {index}: {str(e)}")
                item_results.append(BulkOperationItemResult(
                    index=index,
                    status=BulkItemStatus.FAILED,
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__
                ))
        
        # Commit
        try:
            session.commit()
            for item_result in item_results:
                if item_result.status == BulkItemStatus.PENDING:
                    item_result.status = BulkItemStatus.SUCCESS
        except SQLAlchemyError as e:
            logger.error(f"Bulk upsert commit error: {str(e)}")
            session.rollback()
            
            if atomic:
                for item_result in item_results:
                    if item_result.status == BulkItemStatus.PENDING:
                        item_result.status = BulkItemStatus.FAILED
                        item_result.success = False
                        item_result.error = str(e)
                        item_result.error_type = type(e).__name__
        
        return self._build_result(
            BulkOperationType.UPSERT,
            item_results,
            start_time
        )
    
    @staticmethod
    def _build_result(
        operation: BulkOperationType,
        item_results: List[BulkOperationItemResult],
        start_time: datetime
    ) -> BulkOperationResult:
        """Build final result object"""
        completed_at = datetime.utcnow()
        duration_ms = (completed_at - start_time).total_seconds() * 1000
        
        successful = sum(1 for r in item_results if r.success)
        failed = sum(1 for r in item_results if not r.success)
        total = len(item_results)
        
        errors_summary = [
            f"Item {r.index}: {r.error} ({r.error_type})"
            for r in item_results
            if r.error
        ]
        
        return BulkOperationResult(
            operation=operation,
            total_items=total,
            successful_items=successful,
            failed_items=failed,
            items=item_results,
            duration_ms=duration_ms,
            success_rate=successful / total if total > 0 else 0,
            started_at=start_time,
            completed_at=completed_at,
            errors_summary=errors_summary
        )
