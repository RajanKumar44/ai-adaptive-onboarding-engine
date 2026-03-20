"""
Audit logging service for tracking all database changes.
Provides functionality to log CRUD operations and generate audit trails.
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog, AuditAction
from datetime import datetime
import json


class AuditLogger:
    """
    Service for logging database changes to AuditLog table.
    Tracks who did what, when, and what changed.
    """
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        action: AuditAction,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        """
        Log a single action to the audit trail.
        
        Args:
            db: Database session
            user_id: ID of user performing the action
            table_name: Name of the table being modified
            record_id: ID of the record being modified
            action: Type of action (CREATE, UPDATE, DELETE, etc.)
            old_values: Previous values (for UPDATE/DELETE)
            new_values: New values (for CREATE/UPDATE)
            ip_address: IP address of the request
            user_agent: Browser/client information
            description: Human-readable description
        
        Returns:
            The created AuditLog record
        """
        # Calculate what changed
        changes = None
        if action == AuditAction.UPDATE and old_values and new_values:
            changes = {}
            for key in new_values:
                if old_values.get(key) != new_values.get(key):
                    changes[key] = {
                        "old": old_values.get(key),
                        "new": new_values.get(key),
                    }
        
        audit_log = AuditLog(
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=action.value if isinstance(action, AuditAction) else action,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            description=description,
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def log_create(
        db: Session,
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        new_values: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a CREATE action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.CREATE,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Created {table_name} record #{record_id}",
        )
    
    @staticmethod
    def log_update(
        db: Session,
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log an UPDATE action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.UPDATE,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Updated {table_name} record #{record_id}",
        )
    
    @staticmethod
    def log_delete(
        db: Session,
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        old_values: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a DELETE action (soft delete)."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.DELETE,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Deleted {table_name} record #{record_id}",
        )
    
    @staticmethod
    def log_restore(
        db: Session,
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a RESTORE action (restore soft-deleted record)."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.RESTORE,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Restored {table_name} record #{record_id}",
        )
    
    @staticmethod
    def get_record_history(
        db: Session,
        table_name: str,
        record_id: int,
        limit: int = 100,
    ) -> list:
        """
        Get the audit history for a specific record.
        
        Args:
            db: Database session
            table_name: Name of the table
            record_id: ID of the record
            limit: Maximum number of records to return
        
        Returns:
            List of AuditLog records in chronological order
        """
        return db.query(AuditLog).filter(
            AuditLog.table_name == table_name,
            AuditLog.record_id == record_id,
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_user_activity(
        db: Session,
        user_id: int,
        limit: int = 100,
    ) -> list:
        """
        Get all audit logs for a specific user.
        
        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of records to return
        
        Returns:
            List of AuditLog records
        """
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_table_activity(
        db: Session,
        table_name: str,
        limit: int = 100,
    ) -> list:
        """
        Get all audit logs for a specific table.
        
        Args:
            db: Database session
            table_name: Name of the table
            limit: Maximum number of records to return
        
        Returns:
            List of AuditLog records
        """
        return db.query(AuditLog).filter(
            AuditLog.table_name == table_name,
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
