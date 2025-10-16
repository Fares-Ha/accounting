"""
This module provides the AuditService, which is responsible for creating and managing audit trail entries in the database. The AuditService is used by other services to log important events, such as user login attempts, sales order creation, and stock adjustments.

To use the AuditService, simply import it and call the `create_audit_log` function with the database session, user ID, action, and any relevant details.
"""
from sqlalchemy.orm import Session
from ..database.models import AuditTrail
from datetime import datetime

class AuditService:
    """
    Service for managing audit trails.
    """

    def create_audit_log(self, db: Session, user_id: int, action: str, details: str = None):
        """
        Creates a new audit log entry.
        """
        audit_log = AuditTrail(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log